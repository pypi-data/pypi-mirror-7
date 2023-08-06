# -*- coding:utf-8 -*-
from __future__ import print_function
from unittest import TestCase
import os.path
from datetime import date, timedelta
from korail2 import *
import sys

__author__ = 'sng2c'


class TestKorail(TestCase):
    def setUp(self):
        if not (hasattr(self, "koid") and hasattr(self, "kopw")):
            filepath = "korail_idpw.txt"
            if os.path.exists(filepath):
                with open(filepath) as idpw:
                    self.koid = idpw.readline().strip()
                    self.kopw = idpw.readline().strip()
                self.korail = Korail(self.koid, self.kopw, auto_login=False)
            else:
                raise Exception("No file at %s" % filepath)

        if not self.korail.logined:
            if not self.korail.login():
                raise Exception("Invalid id/pw %s %s" % (self.koid, self.kopw))

    def test_login(self):
        try:
            self.korail.login()
            self.assertTrue(self.korail.logined, "로그인 성공 체크")
        except Exception:
            self.fail(sys.exc_info()[1])

    def test_logout(self):
        try:
            self.korail.logout()
            self.assertFalse(self.korail.logined, "로그아웃 성공 체크")
        except Exception:
            self.fail(sys.exc_info()[1])

    def test_passenger_reduce(self):
        try:
            Passenger()
        except NotImplementedError:
            self.assertTrue(True)
        else:
            self.fail("NotImplementedError must be raised")

        try:
            Passenger.reduce([AdultPassenger, "aaaa"])
        except TypeError:
            self.assertTrue(True)
        else:
            self.fail("TypeError must be raised")

        reduced = Passenger.reduce(
            [AdultPassenger(), AdultPassenger(), AdultPassenger(count=-1), ChildPassenger(count=0),
             SeniorPassenger(count=-1)])
        self.assertEqual(len(reduced), 1)
        for psgr in reduced:
            if isinstance(psgr, AdultPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, ChildPassenger):
                self.fail("ChildPassenger must not appear")
            if isinstance(psgr, SeniorPassenger):
                self.fail("SeniorPassenger must not appear")

        reduced = Passenger.reduce([AdultPassenger(), ChildPassenger(), SeniorPassenger()])
        self.assertEqual(len(reduced), 3)
        for psgr in reduced:
            if isinstance(psgr, AdultPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, ChildPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, SeniorPassenger):
                self.assertEqual(psgr.count, 1)

        reduced = Passenger.reduce(
            [AdultPassenger(), AdultPassenger(), ChildPassenger(), SeniorPassenger(), SeniorPassenger()])
        self.assertEqual(len(reduced), 3)
        for psgr in reduced:
            if isinstance(psgr, AdultPassenger):
                self.assertEqual(psgr.count, 2)
            if isinstance(psgr, ChildPassenger):
                self.assertEqual(psgr.count, 1)
            if isinstance(psgr, SeniorPassenger):
                self.assertEqual(psgr.count, 2)


    def test__result_check(self):
        try:
            self.korail._result_check({})
        except KorailError:
            self.assertTrue(False)
        except Exception:
            self.assertTrue(True)

        try:
            self.korail._result_check({"strResult": "SUCC", "h_msg_cd": "P000", "h_msg_txt": "UNKNOWN"})
        except Exception:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P000", "h_msg_txt": "UNKNOWN"})
        except KorailError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P100", "h_msg_txt": "UNKNOWN"})
        except NoResultsError:
            self.assertTrue(True)
        except KorailError:
            self.assertTrue(False)
        except Exception:
            self.assertTrue(False)

        try:
            self.korail._result_check({"strResult": "FAIL", "h_msg_cd": "P058", "h_msg_txt": "UNKNOWN"})
        except NeedToLoginError:
            self.assertTrue(True)
        except KorailError:
            self.assertTrue(False)
        except Exception:
            self.assertTrue(False)

    def test_search_train(self):
        tomorrow = date.today() + timedelta(days=1)
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000")
        self.assertGreaterEqual(len(trains), 0, "tomorrow train search")
        print(trains)

    # def test_reserve(self):
    # self.skipTest("Same to test_cancel")

    def test_tickets(self):
        tickets = self.korail.tickets()
        self.assertIsInstance(tickets, list)

    def test_reservations(self):
        self.assertIn("P100", NoResultsError)

        try:
            reserves = self.korail.reservations()
            self.assertIsNotNone(reserves, "get reservation list")
            self.assertIsInstance(reserves, list)

            # print reserves
        except Exception:
            e = self.fail(sys.exc_info()[1])
            self.fail(e.message)
            # self.skipTest(e.message)

    def test_reserve_and_cancel(self):
        # self.skipTest("Not implemented")
        tomorrow = date.today() + timedelta(days=1)
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000")

        empty_seats = filter(lambda x: "11" in (x.special_seat, x.general_seat), trains)
        if len(empty_seats) > 0:
            try:
                rsv = self.korail.reserve(empty_seats[0])
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 1, "make a reservation")

                self.korail.cancel(rsv)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 0, "cancel the reservation")
            except SoldOutError:
                self.skipTest("Sold Out")
        else:
            self.skipTest("No Empty Seats tomorrow.")

    def test_reserve_and_cancel2(self):
        # self.skipTest("Not implemented")
        tomorrow = date.today() + timedelta(days=1)
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000")

        empty_seats = filter(lambda x: x.has_special_seat(), trains)
        if len(empty_seats) > 0:
            try:
                rsv = self.korail.reserve(empty_seats[0], option=ReserveOption.SPECIAL_ONLY)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 1, "make a reservation")

                self.korail.cancel(rsv)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 0, "cancel the reservation")
            except SoldOutError:
                self.skipTest("Sold Out")
        else:
            self.skipTest("No Empty Seats tomorrow.")

    def test_reserve_and_cancel_multi(self):
        # self.skipTest("Not implemented")
        tomorrow = date.today() + timedelta(days=1)
        passengers = (
            AdultPassenger(1),
            ChildPassenger(1),
            SeniorPassenger(1),
        )
        trains = self.korail.search_train("서울", "부산", tomorrow.strftime("%Y%m%d"), "100000", passengers=passengers)
        print(trains)
        empty_seats = filter(lambda x: "11" in (x.special_seat, x.general_seat), trains)
        if len(empty_seats) > 0:
            try:
                rsv = self.korail.reserve(empty_seats[0], passengers=passengers)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 1, "make a reservation")

                self.korail.cancel(rsv)
                rsvlist = self.korail.reservations()
                matched = filter(lambda x: x.rsv_id == rsv.rsv_id, rsvlist)
                self.assertEqual(len(matched), 0, "cancel the reservation")
            except SoldOutError:
                self.skipTest("Sold Out")
        else:
            self.skipTest("No Empty Seats tomorrow.")

    def test_cancel_all(self):
        for rsv in self.korail.reservations():
            res = self.korail.cancel(rsv)
            print(repr(rsv) + "\n" + str(res))

        self.assertFalse(self.korail.reservations())

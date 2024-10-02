# Nikari - Event Creation
#
# Written by Martianmellow12

import datetime
from random import randint


#######################
# Event Walker Object #
#######################

class __EventWalker__:

    def __next_occurrence__(self, start, repetition):
        if repetition["type"] == "delta":
            return start + repetition["timedelta"]

    def __init__(self):
        self.events = list()

    def add_event(self, event):
        self.events.append(event)

    def get_events(self, start, end):
        if not self.events: return list()
        results = list()

        # Get all events occurring before the end
        to_check = list()
        for event in self.events:
            if event["start"] < end:
                if event["start"] > start:
                    results.append(event)
                else:
                    to_check.append(event)

        # Extrapolate
        for event in to_check:
            for repetition in event["repetitions"]:
                next_occurrence = event["start"]
                occurrences = repetition["occurrences"]

                while occurrences != 0:
                    next_occurrence = self.__next_occurrence__(next_occurrence, repetition)
                    if (next_occurrence > start) and (next_occurrence < end):
                        results.append(event)


###############
# Event Class #
###############

class Event:

    ####################
    # Internal Methods #
    ####################

    def __get_nth_weekday__(self, datetime_obj, weekday, n):
        iterator = datetime_obj.replace(day=1)
        iters_left = n
        init_month = datetime_obj.month
        while True:
            if iterator.weekday() == weekday:
                iters_left -= 1
            if iters_left <= 0:
                return iterator
            iterator += datetime.timedelta(days=1)
            if iterator.month != init_month:
                return None

    def __get_unique_id__(self, id_list):
        rid = randint(1, len(id_list)*10)
        while rid in id_list: rid = randint(0, len(id_list)*10)
        return rid

    def __reset_occurrence_counters__(self):
        for i in self.repetitions:
            i["occurrence_counter"] = i["occurrences"]

    def __next_occurrence__(self, start, repetition):
        if repetition["type"] == "delta":
            return start + repetition["timedelta"]
        
        if repetition["type"] == "datenum":
            iterator = start + datetime.timedelta(days=1)
            while iterator.day != repetition["datenum"]:
                iterator += datetime.timedelta(days=1)
            return iterator
        
        if repetition["type"] == "dateval":
            iterator = start
            result = self.__get_nth_weekday__(iterator, repetition["dateval"], repetition["ord"])
            while (not result) or (result <= start):
                next_month = iterator.month + 1
                if next_month > 12:
                    iterator = iterator.replace(month=1, year=iterator.year+1)
                else:
                    iterator = iterator.replace(month=next_month)
                result = self.__get_nth_weekday__(iterator, repetition["dateval"], repetition["ord"])
            return result


    ####################
    # Iterator Methods #
    ####################

    def __iter__(self):
        self.__repetition_tracker__ = dict()
        self.__starts_today__ = (self.start + self.duration) > datetime.datetime.now()
        for i in [repetition["id"] for repetition in self.repetitions]:
            self.__repetition_tracker__[i] = self.start

        self.__reset_occurrence_counters__()
        return self

    def __next__(self):
        if self.__starts_today__:
            self.__starts_today__ = False
            return self.start

        next_repetition = None
        repetition_id = -1
        for i in self.repetitions:
            if i["occurrence_counter"] == 0: continue
            temp_occurrence = self.__next_occurrence__(self.__repetition_tracker__[i["id"]], i)
            print(temp_occurrence)
            if (next_repetition == None) or (temp_occurrence < next_repetition):
                next_repetition = temp_occurrence
                repetition_id = i["id"]

        if next_repetition:
            self.__repetition_tracker__[repetition_id] = next_repetition
        return next_repetition


    ################
    # User Methods #
    ################

    def __init__(self, event):
        self.__event__ = event

        self.title = self.__event__["title"]
        self.start = self.__event__["start"]
        self.duration = self.__event__["duration"]
        self.repetitions = self.__event__["repetitions"]
        self.description = self.__event__["description"]
        self.location = self.__event__["location"]
        self.notifications = self.__event__["notifications"]

        # Assign random IDs to each repetition
        for i in self.repetitions: i["id"] = 0
        for i in self.repetitions:
            i["id"] = self.__get_unique_id__([j["id"] for j in self.repetitions])

        self.__reset_occurrence_counters__()

    def to_json(self):
        # TODO(martianmellow12): Implement this
        pass


######################
# Internal Functions #
######################


##################
# User Functions #
##################

def make_event(self, title, start, duration, description="", location=""):
    event = {
        "title" : title,
        "start" : start,
        "duration" : duration,
        "description" : description,
        "location" : location,
        "repetition" : list(),
        "notifications" : list()
    }
    return event

def add_event_notification(self, event, time_diff):
    event["notifications"].append(time_diff)

def add_event_repetition(self, event, rep_type, rep_value, num_occurrences=-1):
    rep = {
        rep_type : rep_value,
        "occurrences" : num_occurrences
    }


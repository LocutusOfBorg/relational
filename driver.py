#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding=UTF-8
# Relational
# Copyright (C) 2010  Salvo "LtWorf" Tomaselli
#
# Relational is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

import os
from sys import exit

from relational import relation, parser, optimizer
from xtermcolor import colorize


COLOR_RED = 0xff0000
COLOR_GREEN = 0x00ff00
COLOR_MAGENTA = 0xff00ff
COLOR_CYAN = 0x00ffff

print(relation)

rels = {}
examples_path = 'samples/'
tests_path = 'test/'


def readfile(fname):
    '''Reads a file as string and returns its content'''
    fd = open(fname)
    expr = fd.read()
    fd.close()
    return expr


def load_relations():
    '''Loads all the relations present in the directory indicated in the
    examples_path variable and stores them in the rels dictionary'''
    print("Loading relations")
    for i in os.listdir(examples_path):
        if i.endswith('.csv'):  # It's a relation, loading it

            # Naming the relation
            relname = i[:-4]

            print ("Loading relation %s with name %s..." % (i, relname))

            rels[relname] = relation.relation('%s%s' % (examples_path, i))
            print('done')


def execute_tests():

    py_bad = 0
    py_good = 0
    py_tot = 0
    q_bad = 0
    q_good = 0
    q_tot = 0
    ex_bad = 0
    ex_good = 0
    ex_tot = 0

    for i in os.listdir(tests_path):
        if i.endswith('.query'):
            q_tot += 1
            if run_test(i[:-6]):
                q_good += 1
            else:
                q_bad += 1
        elif i.endswith('.python'):
            py_tot += 1
            if run_py_test(i[:-7]):
                py_good += 1
            else:
                py_bad += 1
        elif i.endswith('.exec'):
            ex_tot += 1
            if run_exec_test(i[:-5]):
                ex_good += 1
            else:
                ex_bad += 1
    print (colorize("Resume of the results", COLOR_CYAN))

    print (colorize("Query tests", COLOR_MAGENTA))
    print ("Total test count: %d" % q_tot)
    print ("Passed tests: %d" % q_good)
    if q_bad > 0:
        print (colorize("Failed tests count: %d" % q_bad, COLOR_RED))

    print (colorize("Python tests", COLOR_MAGENTA))
    print ("Total test count: %d" % py_tot)
    print ("Passed tests: %d" % py_good)
    if py_bad > 0:
        print (colorize("Failed tests count: %d" % py_bad, COLOR_RED))

    print (colorize("Execute Python tests", COLOR_MAGENTA))
    print ("Total test count: %d" % ex_tot)
    print ("Passed tests: %d" % ex_good)
    if ex_bad > 0:
        print (colorize("Failed tests count: %d" % ex_bad, COLOR_RED))

    print (colorize("Total results", COLOR_CYAN))
    if q_bad + py_bad + ex_bad == 0:
        print (colorize("No failed tests", COLOR_GREEN))
        return 0
    else:
        print (colorize("There are %d failed tests" %
               (py_bad + q_bad + ex_bad), COLOR_RED))
        return 1


def run_exec_test(testname):
    '''Runs a python test, which executes code directly rather than queries'''
    print ("Running python test: " + colorize(testname, COLOR_MAGENTA))

    glob = rels.copy()
    exp_result = {}

    try:
        expr = readfile('%s%s.exec' % (tests_path, testname))
        try:
            exec(expr, glob)  # Evaluating the expression
        except Exception as e:
            print (e)
            raise Exception("")

        expr = readfile('%s%s.result' % (tests_path, testname))
        exp_result = eval(expr, rels)  # Evaluating the expression

        if isinstance(exp_result, dict):
            fields_ok = True

            for i in exp_result:
                fields_ok = fields_ok and glob[i] == exp_result[i]

            if fields_ok:
                print (colorize('Test passed', COLOR_GREEN))
                return True
    except:
        pass
    print (colorize('ERROR', COLOR_RED))
    print (colorize('=====================================', COLOR_RED))
    print ("Expected %s" % exp_result)
    # print ("Got %s" % glob)
    print (colorize('=====================================', COLOR_RED))
    return False


def run_py_test(testname):
    '''Runs a python test, which evaluates expressions directly rather than queries'''
    print ("Running expression python test: " +
           colorize(testname, COLOR_MAGENTA))

    try:

        expr = readfile('%s%s.python' % (tests_path, testname))
        result = eval(expr, rels)  # Evaluating the expression

        expr = readfile('%s%s.result' % (tests_path, testname))
        exp_result = eval(expr, rels)  # Evaluating the expression

        if result == exp_result:
            print (colorize('Test passed', COLOR_GREEN))
            return True
    except:
        pass

    print (colorize('ERROR', COLOR_RED))
    print (colorize('=====================================', COLOR_RED))
    print ("Expected %s" % exp_result)
    print ("Got %s" % result)
    print (colorize('=====================================', COLOR_RED))
    return False


def run_test(testname):
    '''Runs a specific test executing the file
    testname.query
    and comparing the result with
    testname.result
    The query will be executed both unoptimized and
    optimized'''
    print ("Running test: " + colorize(testname, COLOR_MAGENTA))

    query = None
    expr = None
    o_query = None
    o_expr = None
    result_rel = None
    result = None
    o_result = None

    try:
        result_rel = relation.relation('%s%s.result' % (tests_path, testname))

        query = readfile('%s%s.query' % (tests_path, testname)).strip()
        o_query = optimizer.optimize_all(query, rels)

        expr = parser.parse(query)  # Converting expression to python string
        result = eval(expr, rels)  # Evaluating the expression

        o_expr = parser.parse(
            o_query)  # Converting expression to python string
        o_result = eval(o_expr, rels)  # Evaluating the expression

        c_expr = parser.tree(query).toCode()  # Converting to python code
        c_result = eval(c_expr, rels)

        if (o_result == result_rel) and (result == result_rel) and (c_result == result_rel):
            print (colorize('Test passed', COLOR_GREEN))
            return True
    except Exception as inst:
        print (inst)
        pass
    print (colorize('ERROR', COLOR_RED))
    print ("Query: %s -> %s" % (query, expr))
    print ("Optimized query: %s -> %s" % (o_query, o_expr))
    print (colorize('=====================================', COLOR_RED))
    print (colorize("Expected result", COLOR_GREEN))
    print (result_rel)
    print (colorize("Result", COLOR_RED))
    print (result)
    print (colorize("Optimized result", COLOR_RED))
    print (o_result)
    print (colorize("optimized result match %s" %
           str(result_rel == o_result), COLOR_MAGENTA))
    print (colorize("result match %s" %
           str(result == result_rel), COLOR_MAGENTA))
    print (colorize('=====================================', COLOR_RED))
    return False


if __name__ == '__main__':
    print ("-> Starting testsuite for relational")
    load_relations()
    print ("-> Starting tests")
    exit(execute_tests())

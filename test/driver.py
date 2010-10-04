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

from relational import relation, parser, optimizer

import os

rels={}
examples_path='samples/'
tests_path='test/'

def readfile(fname):
    '''Reads a file as string and returns its content'''
    fd=open(fname)
    expr=fd.read()
    fd.close()
    return expr


def load_relations():
    '''Loads all the relations present in the directory indicated in the
    examples_path variable and stores them in the rels dictionary'''
    print "Loading relations"
    for i in os.listdir(examples_path):
        if i.endswith('.csv'): #It's a relation, loading it
            
            #Naming the relation
            relname=i[:-4]
            
            print "Loading relation %s with name %s" % (i,relname)
            
            rels[relname]=relation.relation('%s%s' % (examples_path,i))
            
def execute_tests():
    
    py_bad=0
    py_good=0
    py_tot=0
    q_bad=0
    q_good=0
    q_tot=0
    
    
    for i in os.listdir(tests_path):
        if i.endswith('.query'):
            q_tot+=1
            if run_test(i[:-6]):
                q_good+=1
            else:
                q_bad+=1
        elif i.endswith('.python'):
            py_tot+=1
            if run_py_test(i[:-7]):
                py_good+=1
            else:
                py_bad+=1
    print "\n\033[36;1mResume of the results\033[0m"
    
    print "\n\033[35;1mQuery tests\033[0m"
    print "Total test count: %d" % q_tot
    print "Passed tests: %d" % q_good
    if q_bad>0:
        print "\033[31;1mFailed tests count: %d\033[0m" % q_bad
        
    print "\n\033[35;1mPython tests\033[0m"
    print "Total test count: %d" % py_tot
    print "Passed tests: %d" % py_good
    if py_bad>0:
        print "\033[31;1mFailed tests count: %d\033[0m" % py_bad
    
    print "\n\033[36;1mTotal results\033[0m"
    if q_bad+py_bad==0:
        print "\033[32;1mNo failed tests\033[0m"
    else:
        print "\033[31;1mThere are %d failed tests\033[0m" % (py_bad+q_bad)
        
    
def run_py_test(testname):
    '''Runs a python test, which executes code directly rather than queries'''
    print "Running python test: \033[35;1m%s\033[0m" % testname
    
    expr=readfile('%s%s.python' % (tests_path,testname))
    result=eval(expr,rels) #Evaluating the expression
    
    expr=readfile('%s%s.result' % (tests_path,testname))
    exp_result=eval(expr,rels) #Evaluating the expression
    
    if result==exp_result:
        print "\033[32;1mTest passed\033[0m"
        return True
    else:
        print "\033[31;1mERROR\033[0m"
        print "\033[31;1m=====================================\033[0m"
        print "Expected %s" % exp_result
        print "Got %s" % result
        print "\033[31;1m=====================================\033[0m"
        return False

def run_test(testname):
    '''Runs a specific test executing the file
    testname.query
    and comparing the result with 
    testname.result
    The query will be executed both unoptimized and
    optimized'''
    print "Running test: \033[35;1m%s\033[0m" % testname
    result_rel=relation.relation('%s%s.result' % (tests_path,testname))
    
    query=readfile('%s%s.query' % (tests_path,testname)).strip()
    o_query=optimizer.optimize_all(query,rels)
    
    expr=parser.parse(query)#Converting expression to python code
    result=eval(expr,rels) #Evaluating the expression
    
    o_expr=parser.parse(o_query)#Converting expression to python code
    o_result=eval(o_expr,rels) #Evaluating the expression
    
    
    if (o_result==result_rel) and (result==result_rel):
        print "\033[32;1mTest passed\033[0m"
        return True
    else:
        print "\033[31;1mERROR\033[0m"
        print "Query: %s -> %s" % (query,expr)
        print "Optimized query: %s -> %s" % (o_query,o_expr)
        print "\033[31;1m=====================================\033[0m"
        print "\033[33;1mExpected result\033[0m"
        print result_rel
        print "\033[33;1mResult\033[0m"
        print result
        print "\033[33;1mOptimized result\033[0m"
        print o_result
        print "\033[33;1mResult and optimized result match\033[0m", result==o_result
        print "\033[31;1m=====================================\033[0m"
        return False
        

    
if __name__ == '__main__':
    print "-> Starting testsuite for relational"
    load_relations()
    print "-> Starting tests"
    execute_tests()

testlinkconsole
===============
[![Build Status](https://travis-ci.org/chbrun/testlinkconsole.svg?branch=master)](https://travis-ci.org/chbrun/testlinkconsole)
[![Coverage Status](https://coveralls.io/repos/chbrun/testlinkconsole/badge.png?branch=master)](https://coveralls.io/r/chbrun/testlinkconsole?branch=master)

Testlink console run script test with behat. 

Installation
============

## github
* Clonning repo
* change settings in testlinkclient.cfg : serverUrl and serverKey (serverKey is in testlink)
* Add custom variable in testlink :
  * scriptBehat : type string. It contains path to testcase file.
  * Browsers : type checkbox : Browser to use for testcase

## package pypi
To install testlinkconsole with pip, simply : 
```bash
 pip install testlinkconsole
```

Usage
=====

* start console with
```bash
testlinkconsole
```
* Configure testlink access :
```bash
config
set serverUrl http://[monserver]/
set serverKey [APIKey]
```
>APIKey is on the project page in testlink

* you must setting a project id 
```bash
list projects
set projectid [num of project]
```
* then set a testplan
```
list testplans
set testplanid [num of testplan]
```
* Finally run test plan
```bash
run
```
>You must have behat and selenium installed et run selenium with

```bash
java -jar Selenium-[version].jar
```


Console command
===============
* help   : commands help
* save   : save config (testlinkclient.dfg)
* list   : list projects, testplans, testcases, ...
  * Rmq : list testplans is only available when projectid is valued
* config : affiche les variables de la console
* set    : set variable (projectid, testplanid, ...)
  * Ex : set projectid 1 
* get  : get value of variable
* run  : run test plan

> Note that the console will automatically reload the cfg file at startup, which avoids upgrade variables for each use


TODO
====
- [ ] cmd run : run one test
- [ ] add variable UserAgent 
- [X] plugins system 
- [ ] report system
- [ ] Storage system 
  - [ ] : testlink storage : 50%
  - [ ] : local storage
- [ ] runner plugins
  - [X] : Behat
  - [ ] : Behave

======
PyCvss
======

Easily manipulate and compute scores according to the Common Vulnerability Scoring System

Current status
==============

This library was developped following the specifications at
http://www.first.org/cvss/cvss-guide
and is currently in a stable state.

Features
========

* Compute base, temporal and environmental scores
* Convert from and to short vectors ("AV:N/AC:L/Au:N/C:C/I:C/A:C")
* 100% test coverage
* Pure python

Usage
=====

.. code-block:: python

  c = Cvss()
  # Build from enums:
  c.set(AV.network)
  c.set(E.functional)
  c.set(CDP.low)
  # Or from a vector:
  c = Cvss.from_vector("AV:N/CDP:L/E:F")
  # Get scores.
  c.to_vector())         # "AV:N/CDP:L/E:F"
  c.base_score           # 7.8
  c.temporal_score       # 6.4
  c.environmental_score  # 9.2

Or from a real CVE(2002_0392)

.. code-block:: python

  c = Cvss.from_vector("AV:N/AC:L/Au:N/C:N/I:N/A:C")
  # temp
  c.set(E.functional)
  c.set(RL.official_fix)
  c.set(RC.confirmed)
  # env
  c.set(CDP.high)
  c.set(TD.high)
  c.set(CR.medium)
  c.set(IR.medium)
  c.set(AR.high)
  print(c)
  
  A:C/AC:L/AR:H/AV:N/Au:N/C:N/CDP:H/CR:M/E:F/I:N/IR:M/RC:C/RL:OF/TD:H
  base score                     7.8
    access vector                1.0
    access complexity            0.71
    authentication               0.704
    confidentiality impact       0.0
    integrity impact             0.0
    availability impact          0.66
  
  temporal score                 6.4
    exploitability               0.95
    remediation level            0.87
    report confidence            1.0
  
  environmental score            9.2
    collateral damage potential  0.5
    target distribution          1.0
    confidentiality requirement  1.0
    integrity requirement        1.0
    availability requirement     1.51

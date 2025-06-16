# SQLProcTest
Simple app for testing SQL Server proc changes

Build in Python

Requirement is to build an application for testing stored procedures on a Microsoft SQL Server Database. When provided a proc and  comma delimited list of parameters it will execute a stored procedure and retrieve the results

There are two modes - first is baseline. In this mode it will execute the proc and store the results locally for later comparison.

The second mode is test mode. In this case it will execute the proc, get the results, and compare against the stored copy. Any differences in the two datasets should be displayed..

Language is open. Will run locally on a windows laptop.

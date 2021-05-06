# IS437_Web_App
 Final Project for IS437 - Work in progress..

## Narrative / Outline
The premise fo this application is to have an interface to organize and manage file sharing between members in an organization.
The idea is that a member of the organization will be able to log into the website and view company information that, depending
on their employment level, is only pertinant to them. They will be able to view all other members that are apart of the organization
that use the application. Depenging on employment level they may be able to create, update, or delete users. Application users
will also be able to look at departments and department members. Employment Type determines ability to modify information.
All users will have the ability to modify and manage reports. Which users have access to which reports is dependant on if they
were apart of the report creation process or recieving process. Users will also have access to view events which will provide
information such as if reports were sent, recieved, and viewed. Users can also document these events if they have access to the
reports.


##Login Table
User Type  |  User Email  |  Password
------------ | ------------ | ------------
Admin  |  jp@cu.com  |  12345
Admin  |  tc@cu.com  |  12345
Employee  |  jl@cu.com  |  12345
Employee  |  bh@cu.com  |  12345
Admin  |  js@cu.com  | 12345
Employee  |  sw@cu.com  |  12345
Admin  |  cj@cu.com  |  12345



## SQL Statments For Joining Tables
First Use
```{sql}
SELECT b.Event_ID, b.Event_Date, b.Event_Status, b.Report_ID, a.Report_Name, b.User_ID FROM {tnTwo} a, {tnThree} b 
        WHERE b.Report_ID = a.Report_ID
        AND a.User_ID = %s 
        OR a.Report_Sponsor_ID = %s
```

Second Use
```
SELECT * FROM {tableOne} a, {tableTwo} b 
WHERE a.{fieldOne} = %s 
AND b.User_ID = %s 
OR a.{fieldTwo} = %s 
AND b.User_ID = %s;
```

Third Use
```
SELECT * FROM {tableOne} a, {tableTwo} b 
WHERE a.{fieldOne} = b.{fieldTwo};
```
For the second and third use, this is more of a blanket statement that will work in multiple scenarios. When we add values into 
our 'WHERE' clause, we need to be particular about the order of which we are doing our join statements.

## Schema

!.[relational schema].(/docs/schema.JPG)


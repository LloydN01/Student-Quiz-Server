# CITS3002-Project

CITS3002 Project for Semester 1 2023

To run the program, start in the main directory and run:

1. Run `make` command
2. Open new terminals. You will need one terminal for the TM, and one each for the QBs.
   Each directory also contains a readme reiterating these ideas.

## TM

1. Change directory to TM: `cd TM`
2. Run `python3 TM.py`
   It should print an IP address [IP].

## QB

On both QB terminals:

1. Change directory to QB: `cd QB`

On the first terminal:

2. Run `java QB -p [IP]`

On the second terminal:

2. Run `java QB -j [IP]`

The students taking the test can access the Quiz Website via the IP address of the TM.

## Logging in

1. Login details are stored in the `loginDB.txt` file.
2. Enter the correct username and corresponding password.
   For example, if `'admin': 'password'` is a valid login entry, then the username is `admin` and the password is `password`.

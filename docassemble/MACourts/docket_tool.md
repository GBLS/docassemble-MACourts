# Smart Docketing Tool


NOTE: This deals ONLY with standard docket-number input, i.e., no variations.
Juvenile Court not included.

## DOCKET-NUMBER FORMATS (STANDARD)

1. Superior Court          Example: 1577CV00982

   docket_number[0:1] is the case's filing year
   docket_number[2:3] is the court code
   docket_number[4:5] is the case-type code
   docket_number[6:10] is the 5-digit sequence number

2. District Court          Example: 1670CV000072

   docket_number[0:5] is the same as in the superior-court format.
   docket_number[6:11] is the 6-digit sequence number

3. Boston Municipal Court Example: 1401CV001026

   BMC docket-number format is the same as the district-court format.

4. Housing Court          Example: 15H84CV000436

   docket_number[0:1] is the case's filing year
   docket_number[2:4] is the court code
   docket_number[5:6] is the case-type code
   docket_number[7:12] is the 6-digit sequence number

5. Land Court             Example: 07 TL 001026

   LC docket-number format is the same as the district-court format, except
   without a court code, and the filing year, case-type code, and the
   6-digit sequence number are each separated by a space.

   NOTE: The subsequent (SBQ) land-court case type, however, has a
   unique format. Example: 15 SBQ 00025 09-001
   docket_number[0:6] is the same as in other land-court case types
   docket_number[7:11] is the 5-digit plan number
   docket_number[13:14] is the case's filing month
   docket_number[16:] is the sequence number (likely 3 digits)

6. Probate and Family      Example: ES15A0064AD

   docket_number[0:1] is the site or court code
   docket_number[2:3] is the case's filing year
   docket_number[4] is the case-group code
   docket_number[5:8] is the 4-digit sequence number
   docket_number[9:10] is the case-type code

   I'm not entirely sure what the probate and family court case group adds,
   as the case type already tells us all the information that the case group
   would provide. If we can figure out the case group for each case type,
   this could be used to verify the input docket number. For example, the
   docket number 'ES00A0000XY' should raise an error, because the docket num-
   ber tell us that the case TYPE is 'Proxy Guardianship' ('XY') but that
   the case GROUP is 'Adoption' ('A') instead of 'Proxy Guardianship' ('X').

7. Appeals Court           Example: 2020-P-0874

   The Appeals Court hears cases either as a panel ('P') or in a single-
   justice session ('J'). The docket-number format is four-digit filing year,
   'P' for Panel or 'J' for single justice, then the sequence number, each
   separated by hyphens.

8. Supreme Judicial Court  Example: SJC-13103

   The Supreme Judicial Court docket number is its abbreviation ('SJC') and
   the sequence number separated by a hyphen. No year!

   NOTE: like the Appeals Court, SJC has single-justice sessions, and those
   cases have a unique docket-number format. Example: BD-2021-034.
   The format is case-docket type, four-digit filing year (!), then the
   sequence number, each separated by hyphens. The case-docket types are
   either single justice ('SJ') or bar docket ('BD').

## VARIATIONS

The format is not a requirement. From one case to another, or even within a
the same case, we will see docket numbers that do not follow the above
standard formats.

NOTE: I was able to find uploaded case filings only for superior-court cases,
so the list of variations below, except for superior-court variations, assumes
that other courts follow similar logic in abbreviating or varying the standard
docket-number format. The assumption most definitely stands for district, BMC,
and housing courts, as these courts share the same format as superior courts.

1. Legend for #2 and #3 lists, below:

   'YY' or 'YYYY'  : 2-digit or 4-digit year, e.g., 21 or 2021

   'CC' or 'hCC'   : 2-character court code, which can be letters only (e.g.,
                     ES for Essex Probate and Family Ct.), numbers only
                     (e.g., 77 for Essex Cty. Super. Ct.), or two digits with
                     prefix 'H' for housing courts. As mentioned, land-court
                     docket numbers do not have court codes.

   'TT'            : 2-letter case-type code, e.g., CV for Civil, or 2- to 4-
                     letter case-type code for land court.

   'N'             : Sequence number, e.g., 00001 for the first case in that
                     court of that year and of that case type. The length
                     varies between courts and leading 0s are sometimes
                     removed entirely or all but one.

   'G'             : 1-letter case-group code, applies only to Probate and
                     Family Ct.

   'S'             : Who sits, i.e., whether it is single-justice or panel

2. Standard formats, using above abbreviations:

   · YYCCTTN+          Super. Ct., Dist. Ct., BMC
   · YYhCCN+           Housing Ct. Below, I'll just add '/ hCC'
   · YY TT N+          Land Ct., except SBQ cases
   · YY 'SBQ' P+ MM-N+ Land Ct., SBQ cases, P is Plan Number, MM is Month
   · CCYYGN+TT         Probate and Family Court, G is case-group code
   · YYYY-S-N+         Appeals Court (incl. single-justice)
   · 'SJC'-N+          Supreme Judicial Court (excl. single-justice)
   · 'SJ'-YYYY-N+      Supreme Judicial Court, single-justice matters
   · 'BD'-YYYY-N+      Supreme Judicial Court, single-j. bar-docket matters

3. Variations other than standard format:

   · YYCC-N+ / hCC     Super. Ct., Dist. Ct., BMC / Housing Ct.
   · YYYY-N+           All trial courts
   · YY N+             All trial courts
   · YY-N+             All trial courts
   · YYYY-N+           All trial courts
   · YYCC-TT-N+ / hCC  Super. Ct., Dist. Ct., BMC / Housing Ct.
   · YY-TT-N+          All trial courts
   · YYTTN+[*]         All trial courts
   · TTYY-N+[*]        All trial courts
   · TTYYCC-N+[*]      Super. Ct., Dist. Ct., BMC / Housing Ct.
   · CCYY-(G)N+[*]     Probate Family Ct. with or without case-group code
   · CCTTYY-(G)N+[*]   Probate Family Ct. with or without case-group code

       [*] I have not seen these variations at least in the superior-court
           case filings I've looked at. They are included because they
           follow the 'logic' behind the other observed variations; in fact,
           the first two hypothetical variations, I have seen in federal
           courts.

   Note: I have not seen any variations of appellate docket numbers.

4. EXAMPLE, variations in practice:

   In SpineFrontier, Inc. v. Cummings Props. LLC, No. 1577CV00982 (Essex Cty.
   Super. Ct.), in that single case, we see six docket-number variations
   being used, so we should not assume that the pro se users will (only)
   have the docket number in the standard format:

       (1) 1577-CV-00982   in the defendant's motion
       (2) 15-0982         in the defendant's amended counterclaim
       (3) 15-CV-00982     in the plaintiff's notice of cross-appeal
       (4) 2015-982        in the court's final-judgment order
       (5) 2015-00982      in the court's ruling on MSJ
       (6) 1577CV00982     in the appellate court's notice

## LOCAL NOTES

Local notes are sometimes added to the docket number. For example, in superior
courts, civil cases on specific case-management schedules will have the
relevant track designations suffixed to the docket number. The three
designations are Average Track ('A'), Fast Track ('F'),and Accelerated Track
('X'). There are other local notes, e.g., Business Litigation Session ('BLS').
Some courts may include the presiding judge's initials as local notes.

Only the case-management track designations appear to provide information
useful for pro se litigants. The other notes aid clerks of the court.

## OTHER CONSIDERATIONS

Because of the nature and age of the courts' physical stamps, court-stamped
documents are unlikely to have standardized docket numbers. This is
most relevant at the initial stage of a case, where pro se litigants only
have court-stamped civil-action cover sheet returned from the court after
filing a case or received from the plaintiff along with the complaint.
For example, in Costello v. Needham Bank, the court-stamped civil-action
cover sheet has "20 0735" stamped as the docket number.

## ONLINE CASE ACCESS

Case information and sometimes uploaded PDFs of case filings can be found at
masscourts.org.

Notably (and oddly), the search engine will return with "No Matches Found"
if the docket number is not strictly entered in the standardized format,
including all the leading 0s.

## NOTES ON BELOW CASE-TYPE CODE DICTIONARIES

The 'AD' case-type code in BMC and district courts refers to 'Appeal' but
'Adoption' in probate and family courts. Because of dict key restrictions,
the case-type codes for Probate and Family Courts are in a separate dictionary.
Land Court case-type codes are also in their own dictionary for checking if
the docket number is erroneously missing a court code or if the court code
is missing because it is a case in Land Court.

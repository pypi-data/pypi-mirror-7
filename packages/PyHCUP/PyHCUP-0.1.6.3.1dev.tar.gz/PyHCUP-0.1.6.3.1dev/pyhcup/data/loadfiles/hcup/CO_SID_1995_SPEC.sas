DATA CO95SPEC; 
INFILE EBSPEC LRECL = 152; 

LENGTH 
       SEQ_SID  7
       MRN_S    $17
       PSTCO    4
       BWT      3
       PAY1_X   $17
       CHG1     6
       CHG2     6
       CHG3     6
       CHG4     6
       CHG5     6
       ADATE    4
       DDATE    4
       PRDATE1  4
       ZIP      $5
;


LABEL 
      SEQ_SID ='I:HCUP SID record sequence number'
      MRN_S   ='I:Medical record number (synthetic)'
      PSTCO   ='I:Patient state/county FIPS code'
      BWT     ='I:Birthweight in grams'
      PAY1_X  ='I:Primary exp. payer (from data source)'
      CHG1    ='I:Detailed charges 1 (from data source)'
      CHG2    ='I:Detailed charges 2 (from data source)'
      CHG3    ='I:Detailed charges 3 (from data source)'
      CHG4    ='I:Detailed charges 4 (from data source)'
      CHG5    ='I:Detailed charges 5 (from data source)'
      ADATE   ='I:Admission date'
      DDATE   ='I:Discharge date'
      PRDATE1 ='I:Date of principal procedure'
      ZIP     ='I:Patient zip code'
;


FORMAT
       SEQ_SID   Z13.
       ADATE     DATE7.
       DDATE     DATE7.
       PRDATE1   DATE7.
;


INPUT 
      @1      SEQ_SID   13.
      @14     MRN_S     $CHAR17.
      @31     PSTCO     N5PF.
      @36     BWT       N5PF.
      @41     PAY1_X    $CHAR17.
      @58     CHG1      N12P2F.
      @70     CHG2      N12P2F.
      @82     CHG3      N12P2F.
      @94     CHG4      N12P2F.
      @106    CHG5      N12P2F.
      @118    ADATE     DATE10F.
      @128    DDATE     DATE10F.
      @138    PRDATE1   DATE10F.
      @148    ZIP       $CHAR5.
;



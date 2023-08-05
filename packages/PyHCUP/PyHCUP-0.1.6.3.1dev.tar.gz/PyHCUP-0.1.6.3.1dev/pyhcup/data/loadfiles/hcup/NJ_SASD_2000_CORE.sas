/*******************************************************************            
*   NJ_SASD_2000_CORE.SAS:                                                      
*      THE SAS CODE SHOWN BELOW WILL CONVERT THE ASCII                          
*      OUTPATIENT CORE FILE INTO SAS                                            
*******************************************************************/            
                                                                                
                                                                                
***********************************************;                                
*  Create SAS informats for missing values     ;                                
***********************************************;                                
PROC FORMAT;                                                                    
  INVALUE N2PF                                                                  
    '-9' = .                                                                    
    '-8' = .A                                                                   
    '-6' = .C                                                                   
    '-5' = .N                                                                   
    OTHER = (|2.|)                                                              
  ;                                                                             
  INVALUE N3PF                                                                  
    '-99' = .                                                                   
    '-88' = .A                                                                  
    '-66' = .C                                                                  
    OTHER = (|3.|)                                                              
  ;                                                                             
  INVALUE N4PF                                                                  
    '-999' = .                                                                  
    '-888' = .A                                                                 
    '-666' = .C                                                                 
    OTHER = (|4.|)                                                              
  ;                                                                             
  INVALUE N5PF                                                                  
    '-9999' = .                                                                 
    '-8888' = .A                                                                
    '-6666' = .C                                                                
    OTHER = (|5.|)                                                              
  ;                                                                             
  INVALUE N6PF                                                                  
    '-99999' = .                                                                
    '-88888' = .A                                                               
    '-66666' = .C                                                               
    OTHER = (|6.|)                                                              
  ;                                                                             
  INVALUE N6P2F                                                                 
    '-99.99' = .                                                                
    '-88.88' = .A                                                               
    '-66.66' = .C                                                               
    OTHER = (|6.2|)                                                             
  ;                                                                             
  INVALUE N7P2F                                                                 
    '-999.99' = .                                                               
    '-888.88' = .A                                                              
    '-666.66' = .C                                                              
    OTHER = (|7.2|)                                                             
  ;                                                                             
  INVALUE N8PF                                                                  
    '-9999999' = .                                                              
    '-8888888' = .A                                                             
    '-6666666' = .C                                                             
    OTHER = (|8.|)                                                              
  ;                                                                             
  INVALUE N10PF                                                                 
    '-999999999' = .                                                            
    '-888888888' = .A                                                           
    '-666666666' = .C                                                           
    OTHER = (|10.|)                                                             
  ;                                                                             
  INVALUE N10P4F                                                                
    '-9999.9999' = .                                                            
    '-8888.8888' = .A                                                           
    '-6666.6666' = .C                                                           
    OTHER = (|10.4|)                                                            
  ;                                                                             
  INVALUE DATE10F                                                               
    '-999999999' = .                                                            
    '-888888888' = .A                                                           
    '-666666666' = .C                                                           
    OTHER = (|MMDDYY10.|)                                                       
  ;                                                                             
  INVALUE N12P2F                                                                
    '-99999999.99' = .                                                          
    '-88888888.88' = .A                                                         
    '-66666666.66' = .C                                                         
    OTHER = (|12.2|)                                                            
  ;                                                                             
  INVALUE N15P2F                                                                
    '-99999999999.99' = .                                                       
    '-88888888888.88' = .A                                                      
    '-66666666666.66' = .C                                                      
    OTHER = (|15.2|)                                                            
  ;                                                                             
  RUN;                                                                          
                                                                                
                                                                                
*******************************;                                                
*  Data Step                  *;                                                
*******************************;                                                
DATA NJ_SASDC_2000_CORE;                                                        
INFILE 'NJ_SASDC_2000_CORE.ASC' LRECL = 348;                                    
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  KEY                LENGTH=8                                                   
  LABEL="HCUP record identifier"                                   FORMAT=Z14.  
  AGE                LENGTH=3                                                   
  LABEL="Age in years at admission"                                             
  AGEDAY             LENGTH=3                                                   
  LABEL="Age in days (when age < 1 year)"                                       
  AGEMONTH           LENGTH=3                                                   
  LABEL="Age in months (when age < 11 years)"                                   
  AMONTH             LENGTH=3                                                   
  LABEL="Admission month"                                                       
  ASOURCE            LENGTH=3                                                   
  LABEL="Admission source (uniform)"                                            
  ASOURCE_X          LENGTH=$1                                                  
  LABEL="Admission source (as received from source)"                            
  ATYPE              LENGTH=3                                                   
  LABEL="Admission type"                                                        
  AWEEKEND           LENGTH=3                                                   
  LABEL="Admission day is a weekend"                                            
  DNR                LENGTH=3                                                   
  LABEL="Do not resuscitate indicator"                                          
  DQTR               LENGTH=3                                                   
  LABEL="Discharge quarter"                                                     
  DSHOSPID           LENGTH=$13                                                 
  LABEL="Data source hospital identifier"                                       
  DX1                LENGTH=$5                                                  
  LABEL="Principal diagnosis"                                                   
  DX2                LENGTH=$5                                                  
  LABEL="Diagnosis 2"                                                           
  DX3                LENGTH=$5                                                  
  LABEL="Diagnosis 3"                                                           
  DX4                LENGTH=$5                                                  
  LABEL="Diagnosis 4"                                                           
  DX5                LENGTH=$5                                                  
  LABEL="Diagnosis 5"                                                           
  DX6                LENGTH=$5                                                  
  LABEL="Diagnosis 6"                                                           
  DX7                LENGTH=$5                                                  
  LABEL="Diagnosis 7"                                                           
  DX8                LENGTH=$5                                                  
  LABEL="Diagnosis 8"                                                           
  DX9                LENGTH=$5                                                  
  LABEL="Diagnosis 9"                                                           
  DX10               LENGTH=$5                                                  
  LABEL="Diagnosis 10"                                                          
  DXCCS1             LENGTH=4                                                   
  LABEL="CCS: principal diagnosis"                                              
  DXCCS2             LENGTH=4                                                   
  LABEL="CCS: diagnosis 2"                                                      
  DXCCS3             LENGTH=4                                                   
  LABEL="CCS: diagnosis 3"                                                      
  DXCCS4             LENGTH=4                                                   
  LABEL="CCS: diagnosis 4"                                                      
  DXCCS5             LENGTH=4                                                   
  LABEL="CCS: diagnosis 5"                                                      
  DXCCS6             LENGTH=4                                                   
  LABEL="CCS: diagnosis 6"                                                      
  DXCCS7             LENGTH=4                                                   
  LABEL="CCS: diagnosis 7"                                                      
  DXCCS8             LENGTH=4                                                   
  LABEL="CCS: diagnosis 8"                                                      
  DXCCS9             LENGTH=4                                                   
  LABEL="CCS: diagnosis 9"                                                      
  DXCCS10            LENGTH=4                                                   
  LABEL="CCS: diagnosis 10"                                                     
  FEMALE             LENGTH=3                                                   
  LABEL="Indicator of sex"                                                      
  HISPANIC_X         LENGTH=$1                                                  
  LABEL="Hispanic ethnicity (as received from source)"                          
  HOSPST             LENGTH=$2                                                  
  LABEL="Hospital state postal code"                                            
  LOS                LENGTH=4                                                   
  LABEL="Length of stay (cleaned)"                                              
  LOS_X              LENGTH=4                                                   
  LABEL="Length of stay (as received from source)"                              
  MDID_S             LENGTH=$16                                                 
  LABEL="Attending physician number (synthetic)"                                
  MDSPEC             LENGTH=$1                                                  
  LABEL="Attending Physician specialty (as received from source)"               
  MRN_S              LENGTH=$17                                                 
  LABEL="Medical record number (synthetic)"                                     
  NDX                LENGTH=3                                                   
  LABEL="Number of diagnoses on this record"                                    
  NEOMAT             LENGTH=3                                                   
  LABEL="Neonatal and/or maternal DX and/or PR"                                 
  NPR                LENGTH=3                                                   
  LABEL="Number of procedures on this record"                                   
  PAY1               LENGTH=3                                                   
  LABEL="Primary expected payer (uniform)"                                      
  PAY2               LENGTH=3                                                   
  LABEL="Secondary expected payer (uniform)"                                    
  PAY1_X             LENGTH=$3                                                  
  LABEL="Primary expected payer (as received from source)"                      
  PAY2_X             LENGTH=$3                                                  
  LABEL="Secondary expected payer (as received from source)"                    
  PAY3_X             LENGTH=$3                                                  
  LABEL="Tertiary expected payer (as received from source)"                     
  PR1                LENGTH=$4                                                  
  LABEL="Principal procedure"                                                   
  PR2                LENGTH=$4                                                  
  LABEL="Procedure 2"                                                           
  PR3                LENGTH=$4                                                  
  LABEL="Procedure 3"                                                           
  PR4                LENGTH=$4                                                  
  LABEL="Procedure 4"                                                           
  PR5                LENGTH=$4                                                  
  LABEL="Procedure 5"                                                           
  PR6                LENGTH=$4                                                  
  LABEL="Procedure 6"                                                           
  PR7                LENGTH=$4                                                  
  LABEL="Procedure 7"                                                           
  PR8                LENGTH=$4                                                  
  LABEL="Procedure 8"                                                           
  PRCCS1             LENGTH=3                                                   
  LABEL="CCS: principal procedure"                                              
  PRCCS2             LENGTH=3                                                   
  LABEL="CCS: procedure 2"                                                      
  PRCCS3             LENGTH=3                                                   
  LABEL="CCS: procedure 3"                                                      
  PRCCS4             LENGTH=3                                                   
  LABEL="CCS: procedure 4"                                                      
  PRCCS5             LENGTH=3                                                   
  LABEL="CCS: procedure 5"                                                      
  PRCCS6             LENGTH=3                                                   
  LABEL="CCS: procedure 6"                                                      
  PRCCS7             LENGTH=3                                                   
  LABEL="CCS: procedure 7"                                                      
  PRCCS8             LENGTH=3                                                   
  LABEL="CCS: procedure 8"                                                      
  PRDAY1             LENGTH=4                                                   
  LABEL="Number of days from admission to PR1"                                  
  PRDAY2             LENGTH=4                                                   
  LABEL="Number of days from admission to PR2"                                  
  PRDAY3             LENGTH=4                                                   
  LABEL="Number of days from admission to PR3"                                  
  PRDAY4             LENGTH=4                                                   
  LABEL="Number of days from admission to PR4"                                  
  PRDAY5             LENGTH=4                                                   
  LABEL="Number of days from admission to PR5"                                  
  PRDAY6             LENGTH=4                                                   
  LABEL="Number of days from admission to PR6"                                  
  PRDAY7             LENGTH=4                                                   
  LABEL="Number of days from admission to PR7"                                  
  PRDAY8             LENGTH=4                                                   
  LABEL="Number of days from admission to PR8"                                  
  PSTCO              LENGTH=4                                                   
  LABEL="Patient state/county FIPS code"                                        
  RACE               LENGTH=3                                                   
  LABEL="Race (uniform)"                                                        
  RACE_X             LENGTH=$1                                                  
  LABEL="Race (as received from source)"                                        
  READMIT            LENGTH=3                                                   
  LABEL="Readmission"                                                           
  SURGID_S           LENGTH=$16                                                 
  LABEL="Primary surgeon number (synthetic)"                                    
  TOTCHG             LENGTH=6                                                   
  LABEL="Total charges (cleaned)"                                               
  TOTCHG_X           LENGTH=7                                                   
  LABEL="Total charges (as received from source)"                               
  YEAR               LENGTH=3                                                   
  LABEL="Calendar year"                                                         
  ZIP                LENGTH=$5                                                  
  LABEL="Patient zip code"                                                      
;                                                                               
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      KEY                 14.                                           
      @15     AGE                 N3PF.                                         
      @18     AGEDAY              N3PF.                                         
      @21     AGEMONTH            N3PF.                                         
      @24     AMONTH              N2PF.                                         
      @26     ASOURCE             N2PF.                                         
      @28     ASOURCE_X           $CHAR1.                                       
      @29     ATYPE               N2PF.                                         
      @31     AWEEKEND            N2PF.                                         
      @33     DNR                 N2PF.                                         
      @35     DQTR                N2PF.                                         
      @37     DSHOSPID            $CHAR13.                                      
      @50     DX1                 $CHAR5.                                       
      @55     DX2                 $CHAR5.                                       
      @60     DX3                 $CHAR5.                                       
      @65     DX4                 $CHAR5.                                       
      @70     DX5                 $CHAR5.                                       
      @75     DX6                 $CHAR5.                                       
      @80     DX7                 $CHAR5.                                       
      @85     DX8                 $CHAR5.                                       
      @90     DX9                 $CHAR5.                                       
      @95     DX10                $CHAR5.                                       
      @100    DXCCS1              N4PF.                                         
      @104    DXCCS2              N4PF.                                         
      @108    DXCCS3              N4PF.                                         
      @112    DXCCS4              N4PF.                                         
      @116    DXCCS5              N4PF.                                         
      @120    DXCCS6              N4PF.                                         
      @124    DXCCS7              N4PF.                                         
      @128    DXCCS8              N4PF.                                         
      @132    DXCCS9              N4PF.                                         
      @136    DXCCS10             N4PF.                                         
      @140    FEMALE              N2PF.                                         
      @142    HISPANIC_X          $CHAR1.                                       
      @143    HOSPST              $CHAR2.                                       
      @145    LOS                 N5PF.                                         
      @150    LOS_X               N6PF.                                         
      @156    MDID_S              $CHAR16.                                      
      @172    MDSPEC              $CHAR1.                                       
      @173    MRN_S               $CHAR17.                                      
      @190    NDX                 N2PF.                                         
      @192    NEOMAT              N2PF.                                         
      @194    NPR                 N2PF.                                         
      @196    PAY1                N2PF.                                         
      @198    PAY2                N2PF.                                         
      @200    PAY1_X              $CHAR3.                                       
      @203    PAY2_X              $CHAR3.                                       
      @206    PAY3_X              $CHAR3.                                       
      @209    PR1                 $CHAR4.                                       
      @213    PR2                 $CHAR4.                                       
      @217    PR3                 $CHAR4.                                       
      @221    PR4                 $CHAR4.                                       
      @225    PR5                 $CHAR4.                                       
      @229    PR6                 $CHAR4.                                       
      @233    PR7                 $CHAR4.                                       
      @237    PR8                 $CHAR4.                                       
      @241    PRCCS1              N3PF.                                         
      @244    PRCCS2              N3PF.                                         
      @247    PRCCS3              N3PF.                                         
      @250    PRCCS4              N3PF.                                         
      @253    PRCCS5              N3PF.                                         
      @256    PRCCS6              N3PF.                                         
      @259    PRCCS7              N3PF.                                         
      @262    PRCCS8              N3PF.                                         
      @265    PRDAY1              N3PF.                                         
      @268    PRDAY2              N3PF.                                         
      @271    PRDAY3              N3PF.                                         
      @274    PRDAY4              N3PF.                                         
      @277    PRDAY5              N3PF.                                         
      @280    PRDAY6              N3PF.                                         
      @283    PRDAY7              N3PF.                                         
      @286    PRDAY8              N3PF.                                         
      @289    PSTCO               N5PF.                                         
      @294    RACE                N2PF.                                         
      @296    RACE_X              $CHAR1.                                       
      @297    READMIT             N2PF.                                         
      @299    SURGID_S            $CHAR16.                                      
      @315    TOTCHG              N10PF.                                        
      @325    TOTCHG_X            N15P2F.                                       
      @340    YEAR                N4PF.                                         
      @344    ZIP                 $CHAR5.                                       
;                                                                               
                                                                                
                                                                                
RUN;

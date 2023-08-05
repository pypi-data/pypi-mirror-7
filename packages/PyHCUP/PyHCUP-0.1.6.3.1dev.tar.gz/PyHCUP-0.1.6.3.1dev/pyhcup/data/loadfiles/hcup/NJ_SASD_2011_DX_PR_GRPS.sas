/*******************************************************************            
*   NJ_SASD_2011_DX_PR_GRPS.SAS:                                                
*      THE SAS CODE SHOWN BELOW WILL LOAD THE ASCII                             
*      OUTPATIENT SASD DX_PR_GRPS FILE INTO SAS                                 
*      INPATIENT STAY DX_PR_GRPS FILE INTO SAS                                  
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
  INVALUE N4P1F                                                                 
    '-9.9' = .                                                                  
    '-8.8' = .A                                                                 
    '-6.6' = .C                                                                 
    OTHER = (|4.1|)                                                             
  ;                                                                             
  INVALUE N5PF                                                                  
    '-9999' = .                                                                 
    '-8888' = .A                                                                
    '-6666' = .C                                                                
    OTHER = (|5.|)                                                              
  ;                                                                             
  INVALUE N5P2F                                                                 
    '-9.99' = .                                                                 
    '-8.88' = .A                                                                
    '-6.66' = .C                                                                
    OTHER = (|5.2|)                                                             
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
  INVALUE N7P4F                                                                 
    '-9.9999' = .                                                               
    '-8.8888' = .A                                                              
    '-6.6666' = .C                                                              
    OTHER = (|7.4|)                                                             
  ;                                                                             
  INVALUE N8PF                                                                  
    '-9999999' = .                                                              
    '-8888888' = .A                                                             
    '-6666666' = .C                                                             
    OTHER = (|8.|)                                                              
  ;                                                                             
  INVALUE N8P2F                                                                 
    '-9999.99' = .                                                              
    '-8888.88' = .A                                                             
    '-6666.66' = .C                                                             
    OTHER = (|8.2|)                                                             
  ;                                                                             
  INVALUE N9PF                                                                  
    '-99999999' = .                                                             
    '-88888888' = .A                                                            
    '-66666666' = .C                                                            
    OTHER = (|9.|)                                                              
  ;                                                                             
  INVALUE N9P2F                                                                 
    '-99999.99' = .                                                             
    '-88888.88' = .A                                                            
    '-66666.66' = .C                                                            
    OTHER = (|9.2|)                                                             
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
  INVALUE N10P5F                                                                
    '-999.99999' = .                                                            
    '-888.88888' = .A                                                           
    '-666.66666' = .C                                                           
    OTHER = (|10.5|)                                                            
  ;                                                                             
  INVALUE DATE10F                                                               
    '-999999999' = .                                                            
    '-888888888' = .A                                                           
    '-666666666' = .C                                                           
    OTHER = (|MMDDYY10.|)                                                       
  ;                                                                             
  INVALUE N11PF                                                                 
    '-9999999999' = .                                                           
    '-8888888888' = .A                                                          
    '-6666666666' = .C                                                          
    OTHER = (|11.|)                                                             
  ;                                                                             
  INVALUE N12P2F                                                                
    '-99999999.99' = .                                                          
    '-88888888.88' = .A                                                         
    '-66666666.66' = .C                                                         
    OTHER = (|12.2|)                                                            
  ;                                                                             
  INVALUE N12P5F                                                                
    '-99999.99999' = .                                                          
    '-88888.88888' = .A                                                         
    '-66666.66666' = .C                                                         
    OTHER = (|12.5|)                                                            
  ;                                                                             
  INVALUE N13PF                                                                 
    '-999999999999' = .                                                         
    '-888888888888' = .A                                                        
    '-666666666666' = .C                                                        
    OTHER = (|13.|)                                                             
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
DATA NJ_SASDC_2011_DX_PR_GRPS;                                                  
INFILE 'NJ_SASD_2011_DX_PR_GRPS.ASC' LRECL = 748;                               
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  CHRON1                     LENGTH=3                                           
  LABEL="Chronic condition indicator 1"                                         
                                                                                
  CHRON2                     LENGTH=3                                           
  LABEL="Chronic condition indicator 2"                                         
                                                                                
  CHRON3                     LENGTH=3                                           
  LABEL="Chronic condition indicator 3"                                         
                                                                                
  CHRON4                     LENGTH=3                                           
  LABEL="Chronic condition indicator 4"                                         
                                                                                
  CHRON5                     LENGTH=3                                           
  LABEL="Chronic condition indicator 5"                                         
                                                                                
  CHRON6                     LENGTH=3                                           
  LABEL="Chronic condition indicator 6"                                         
                                                                                
  CHRON7                     LENGTH=3                                           
  LABEL="Chronic condition indicator 7"                                         
                                                                                
  CHRON8                     LENGTH=3                                           
  LABEL="Chronic condition indicator 8"                                         
                                                                                
  CHRON9                     LENGTH=3                                           
  LABEL="Chronic condition indicator 9"                                         
                                                                                
  CHRON10                    LENGTH=3                                           
  LABEL="Chronic condition indicator 10"                                        
                                                                                
  CHRON11                    LENGTH=3                                           
  LABEL="Chronic condition indicator 11"                                        
                                                                                
  CHRON12                    LENGTH=3                                           
  LABEL="Chronic condition indicator 12"                                        
                                                                                
  CHRON13                    LENGTH=3                                           
  LABEL="Chronic condition indicator 13"                                        
                                                                                
  CHRON14                    LENGTH=3                                           
  LABEL="Chronic condition indicator 14"                                        
                                                                                
  CHRON15                    LENGTH=3                                           
  LABEL="Chronic condition indicator 15"                                        
                                                                                
  CHRON16                    LENGTH=3                                           
  LABEL="Chronic condition indicator 16"                                        
                                                                                
  CHRON17                    LENGTH=3                                           
  LABEL="Chronic condition indicator 17"                                        
                                                                                
  CHRON18                    LENGTH=3                                           
  LABEL="Chronic condition indicator 18"                                        
                                                                                
  CHRON19                    LENGTH=3                                           
  LABEL="Chronic condition indicator 19"                                        
                                                                                
  CHRON20                    LENGTH=3                                           
  LABEL="Chronic condition indicator 20"                                        
                                                                                
  CHRON21                    LENGTH=3                                           
  LABEL="Chronic condition indicator 21"                                        
                                                                                
  CHRON22                    LENGTH=3                                           
  LABEL="Chronic condition indicator 22"                                        
                                                                                
  CHRON23                    LENGTH=3                                           
  LABEL="Chronic condition indicator 23"                                        
                                                                                
  CHRON24                    LENGTH=3                                           
  LABEL="Chronic condition indicator 24"                                        
                                                                                
  CHRONB1                    LENGTH=3                                           
  LABEL="Chronic condition body system 1"                                       
                                                                                
  CHRONB2                    LENGTH=3                                           
  LABEL="Chronic condition body system 2"                                       
                                                                                
  CHRONB3                    LENGTH=3                                           
  LABEL="Chronic condition body system 3"                                       
                                                                                
  CHRONB4                    LENGTH=3                                           
  LABEL="Chronic condition body system 4"                                       
                                                                                
  CHRONB5                    LENGTH=3                                           
  LABEL="Chronic condition body system 5"                                       
                                                                                
  CHRONB6                    LENGTH=3                                           
  LABEL="Chronic condition body system 6"                                       
                                                                                
  CHRONB7                    LENGTH=3                                           
  LABEL="Chronic condition body system 7"                                       
                                                                                
  CHRONB8                    LENGTH=3                                           
  LABEL="Chronic condition body system 8"                                       
                                                                                
  CHRONB9                    LENGTH=3                                           
  LABEL="Chronic condition body system 9"                                       
                                                                                
  CHRONB10                   LENGTH=3                                           
  LABEL="Chronic condition body system 10"                                      
                                                                                
  CHRONB11                   LENGTH=3                                           
  LABEL="Chronic condition body system 11"                                      
                                                                                
  CHRONB12                   LENGTH=3                                           
  LABEL="Chronic condition body system 12"                                      
                                                                                
  CHRONB13                   LENGTH=3                                           
  LABEL="Chronic condition body system 13"                                      
                                                                                
  CHRONB14                   LENGTH=3                                           
  LABEL="Chronic condition body system 14"                                      
                                                                                
  CHRONB15                   LENGTH=3                                           
  LABEL="Chronic condition body system 15"                                      
                                                                                
  CHRONB16                   LENGTH=3                                           
  LABEL="Chronic condition body system 16"                                      
                                                                                
  CHRONB17                   LENGTH=3                                           
  LABEL="Chronic condition body system 17"                                      
                                                                                
  CHRONB18                   LENGTH=3                                           
  LABEL="Chronic condition body system 18"                                      
                                                                                
  CHRONB19                   LENGTH=3                                           
  LABEL="Chronic condition body system 19"                                      
                                                                                
  CHRONB20                   LENGTH=3                                           
  LABEL="Chronic condition body system 20"                                      
                                                                                
  CHRONB21                   LENGTH=3                                           
  LABEL="Chronic condition body system 21"                                      
                                                                                
  CHRONB22                   LENGTH=3                                           
  LABEL="Chronic condition body system 22"                                      
                                                                                
  CHRONB23                   LENGTH=3                                           
  LABEL="Chronic condition body system 23"                                      
                                                                                
  CHRONB24                   LENGTH=3                                           
  LABEL="Chronic condition body system 24"                                      
                                                                                
  DXMCCS1                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 1"                                         
                                                                                
  DXMCCS2                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 2"                                         
                                                                                
  DXMCCS3                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 3"                                         
                                                                                
  DXMCCS4                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 4"                                         
                                                                                
  DXMCCS5                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 5"                                         
                                                                                
  DXMCCS6                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 6"                                         
                                                                                
  DXMCCS7                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 7"                                         
                                                                                
  DXMCCS8                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 8"                                         
                                                                                
  DXMCCS9                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 9"                                         
                                                                                
  DXMCCS10                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 10"                                        
                                                                                
  DXMCCS11                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 11"                                        
                                                                                
  DXMCCS12                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 12"                                        
                                                                                
  DXMCCS13                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 13"                                        
                                                                                
  DXMCCS14                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 14"                                        
                                                                                
  DXMCCS15                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 15"                                        
                                                                                
  DXMCCS16                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 16"                                        
                                                                                
  DXMCCS17                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 17"                                        
                                                                                
  DXMCCS18                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 18"                                        
                                                                                
  DXMCCS19                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 19"                                        
                                                                                
  DXMCCS20                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 20"                                        
                                                                                
  DXMCCS21                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 21"                                        
                                                                                
  DXMCCS22                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 22"                                        
                                                                                
  DXMCCS23                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 23"                                        
                                                                                
  DXMCCS24                   LENGTH=$11                                         
  LABEL="Multi-Level CCS:  Diagnosis 24"                                        
                                                                                
  E_MCCS1                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 1"                                            
                                                                                
  E_MCCS2                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 2"                                            
                                                                                
  E_MCCS3                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 3"                                            
                                                                                
  E_MCCS4                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 4"                                            
                                                                                
  E_MCCS5                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 5"                                            
                                                                                
  E_MCCS6                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 6"                                            
                                                                                
  E_MCCS7                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 7"                                            
                                                                                
  E_MCCS8                    LENGTH=$11                                         
  LABEL="Multi-Level CCS:  E Code 8"                                            
                                                                                
  INJURY                     LENGTH=3                                           
  LABEL=                                                                        
                                                                                
"Injury diagnosis reported on record (1:DX1 is an injury; 2:DX2+ is an injury; 0
:No injury)"                                                                    
                                                                                
  INJURY_CUT                 LENGTH=3                                           
  LABEL="Injury by cutting or piercing (by E codes)"                            
                                                                                
  INJURY_DROWN               LENGTH=3                                           
  LABEL="Injury by drowning or submersion (by E codes)"                         
                                                                                
  INJURY_FALL                LENGTH=3                                           
  LABEL="Injury by falling (by E codes)"                                        
                                                                                
  INJURY_FIRE                LENGTH=3                                           
  LABEL="Injury by fire, flame or hot object (by E codes)"                      
                                                                                
  INJURY_FIREARM             LENGTH=3                                           
  LABEL="Injury by firearm (by E codes)"                                        
                                                                                
  INJURY_MACHINERY           LENGTH=3                                           
  LABEL="Injury by machinery (by E codes)"                                      
                                                                                
  INJURY_MVT                 LENGTH=3                                           
  LABEL="Injury involving motor vehicle traffic (by E codes)"                   
                                                                                
  INJURY_NATURE              LENGTH=3                                           
  LABEL="Injury involving nature or environmental factors (by E codes)"         
                                                                                
  INJURY_POISON              LENGTH=3                                           
  LABEL="Injury by poison (by E codes)"                                         
                                                                                
  INJURY_STRUCK              LENGTH=3                                           
  LABEL="Injury from being struck by or against (by E codes)"                   
                                                                                
  INJURY_SUFFOCATION         LENGTH=3                                           
  LABEL="Injury by suffocation (by E codes)"                                    
                                                                                
  INTENT_ASSAULT             LENGTH=3                                           
  LABEL="Injury by assault indicated on the record (by E codes)"                
                                                                                
  INTENT_SELF_HARM           LENGTH=3                                           
  LABEL=                                                                        
  "Intentional self harm indicated on the record (by diagnosis and/or E codes)" 
                                                                                
  INTENT_UNINTENTIONAL       LENGTH=3                                           
  LABEL="Unintentional injury indicated on the record (by E codes)"             
                                                                                
  KEY                        LENGTH=8                 FORMAT=Z18.               
  LABEL="HCUP record identifier"                                                
                                                                                
  MULTINJURY                 LENGTH=3                                           
  LABEL="More than one injury diagnosis reported on record"                     
                                                                                
  PCLASS1                    LENGTH=3                                           
  LABEL="Procedure class 1"                                                     
                                                                                
  PCLASS2                    LENGTH=3                                           
  LABEL="Procedure class 2"                                                     
                                                                                
  PCLASS3                    LENGTH=3                                           
  LABEL="Procedure class 3"                                                     
                                                                                
  PCLASS4                    LENGTH=3                                           
  LABEL="Procedure class 4"                                                     
                                                                                
  PCLASS5                    LENGTH=3                                           
  LABEL="Procedure class 5"                                                     
                                                                                
  PCLASS6                    LENGTH=3                                           
  LABEL="Procedure class 6"                                                     
                                                                                
  PCLASS7                    LENGTH=3                                           
  LABEL="Procedure class 7"                                                     
                                                                                
  PCLASS8                    LENGTH=3                                           
  LABEL="Procedure class 8"                                                     
                                                                                
  PCLASS9                    LENGTH=3                                           
  LABEL="Procedure class 9"                                                     
                                                                                
  PCLASS10                   LENGTH=3                                           
  LABEL="Procedure class 10"                                                    
                                                                                
  PCLASS11                   LENGTH=3                                           
  LABEL="Procedure class 11"                                                    
                                                                                
  PCLASS12                   LENGTH=3                                           
  LABEL="Procedure class 12"                                                    
                                                                                
  PCLASS13                   LENGTH=3                                           
  LABEL="Procedure class 13"                                                    
                                                                                
  PCLASS14                   LENGTH=3                                           
  LABEL="Procedure class 14"                                                    
                                                                                
  PCLASS15                   LENGTH=3                                           
  LABEL="Procedure class 15"                                                    
                                                                                
  PCLASS16                   LENGTH=3                                           
  LABEL="Procedure class 16"                                                    
                                                                                
  PCLASS17                   LENGTH=3                                           
  LABEL="Procedure class 17"                                                    
                                                                                
  PCLASS18                   LENGTH=3                                           
  LABEL="Procedure class 18"                                                    
                                                                                
  PCLASS19                   LENGTH=3                                           
  LABEL="Procedure class 19"                                                    
                                                                                
  PRMCCS1                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 1"                                         
                                                                                
  PRMCCS2                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 2"                                         
                                                                                
  PRMCCS3                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 3"                                         
                                                                                
  PRMCCS4                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 4"                                         
                                                                                
  PRMCCS5                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 5"                                         
                                                                                
  PRMCCS6                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 6"                                         
                                                                                
  PRMCCS7                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 7"                                         
                                                                                
  PRMCCS8                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 8"                                         
                                                                                
  PRMCCS9                    LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 9"                                         
                                                                                
  PRMCCS10                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 10"                                        
                                                                                
  PRMCCS11                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 11"                                        
                                                                                
  PRMCCS12                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 12"                                        
                                                                                
  PRMCCS13                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 13"                                        
                                                                                
  PRMCCS14                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 14"                                        
                                                                                
  PRMCCS15                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 15"                                        
                                                                                
  PRMCCS16                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 16"                                        
                                                                                
  PRMCCS17                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 17"                                        
                                                                                
  PRMCCS18                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 18"                                        
                                                                                
  PRMCCS19                   LENGTH=$8                                          
  LABEL="Multi-Level CCS:  Procedure 19"                                        
                                                                                
  U_BLOOD                    LENGTH=3                                           
  LABEL="Utilization Flag: Blood"                                               
                                                                                
  U_CATH                     LENGTH=3                                           
  LABEL="Utilization Flag: Cardiac Catheterization Lab"                         
                                                                                
  U_CCU                      LENGTH=3                                           
  LABEL="Utilization Flag: Coronary Care Unit (CCU)"                            
                                                                                
  U_CHESTXRAY                LENGTH=3                                           
  LABEL="Utilization Flag: Chest X-Ray"                                         
                                                                                
  U_CTSCAN                   LENGTH=3                                           
  LABEL="Utilization Flag: Computed Tomography Scan"                            
                                                                                
  U_DIALYSIS                 LENGTH=3                                           
  LABEL="Utilization Flag: Renal Dialysis"                                      
                                                                                
  U_ECHO                     LENGTH=3                                           
  LABEL="Utilization Flag: Echocardiology"                                      
                                                                                
  U_ED                       LENGTH=3                                           
  LABEL="Utilization Flag: Emergency Room"                                      
                                                                                
  U_EEG                      LENGTH=3                                           
  LABEL="Utilization Flag: Electroencephalogram"                                
                                                                                
  U_EKG                      LENGTH=3                                           
  LABEL="Utilization Flag: Electrocardiogram"                                   
                                                                                
  U_EPO                      LENGTH=3                                           
  LABEL="Utilization Flag: EPO"                                                 
                                                                                
  U_ICU                      LENGTH=3                                           
  LABEL="Utilization Flag: Intensive Care Unit (ICU)"                           
                                                                                
  U_LITHOTRIPSY              LENGTH=3                                           
  LABEL="Utilization Flag: Lithotripsy"                                         
                                                                                
  U_MHSA                     LENGTH=3                                           
  LABEL="Utilization Flag: Mental Health and Substance Abuse"                   
                                                                                
  U_MRT                      LENGTH=3                                           
  LABEL="Utilization Flag: Medical Resonance Technology"                        
                                                                                
  U_NEWBN2L                  LENGTH=3                                           
  LABEL="Utilization Flag: Nursery Level II"                                    
                                                                                
  U_NEWBN3L                  LENGTH=3                                           
  LABEL="Utilization Flag: Nursery Level III"                                   
                                                                                
  U_NEWBN4L                  LENGTH=3                                           
  LABEL="Utilization Flag: Nursery Level IV"                                    
                                                                                
  U_NUCMED                   LENGTH=3                                           
  LABEL="Utilization Flag: Nuclear Medicine"                                    
                                                                                
  U_OBSERVATION              LENGTH=3                                           
  LABEL="Utilization Flag: Observation Room"                                    
                                                                                
  U_OCCTHERAPY               LENGTH=3                                           
  LABEL="Utilization Flag: Occupational Therapy"                                
                                                                                
  U_ORGANACQ                 LENGTH=3                                           
  LABEL="Utilization Flag: Organ Acquisition"                                   
                                                                                
  U_OTHIMPLANTS              LENGTH=3                                           
  LABEL="Utilization Flag: Other Implants"                                      
                                                                                
  U_PACEMAKER                LENGTH=3                                           
  LABEL="Utilization Flag: Pacemaker"                                           
                                                                                
  U_PHYTHERAPY               LENGTH=3                                           
  LABEL="Utilization Flag: Physical Therapy"                                    
                                                                                
  U_RADTHERAPY               LENGTH=3                                           
  LABEL=                                                                        
  "Utilization Flag: Radiology - Therapeutic and/or Chemotherapy Administration"
                                                                                
  U_RESPTHERAPY              LENGTH=3                                           
  LABEL="Utilization Flag: Respiratory Services"                                
                                                                                
  U_SPEECHTHERAPY            LENGTH=3                                           
  LABEL="Utilization Flag: Speech - Language Pathology"                         
                                                                                
  U_STRESS                   LENGTH=3                                           
  LABEL="Utilization Flag: Cardiac Stress Test"                                 
                                                                                
  U_ULTRASOUND               LENGTH=3                                           
  LABEL="Utilization Flag: Ultrasound"                                          
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      CHRON1                   N2PF.                                    
      @3      CHRON2                   N2PF.                                    
      @5      CHRON3                   N2PF.                                    
      @7      CHRON4                   N2PF.                                    
      @9      CHRON5                   N2PF.                                    
      @11     CHRON6                   N2PF.                                    
      @13     CHRON7                   N2PF.                                    
      @15     CHRON8                   N2PF.                                    
      @17     CHRON9                   N2PF.                                    
      @19     CHRON10                  N2PF.                                    
      @21     CHRON11                  N2PF.                                    
      @23     CHRON12                  N2PF.                                    
      @25     CHRON13                  N2PF.                                    
      @27     CHRON14                  N2PF.                                    
      @29     CHRON15                  N2PF.                                    
      @31     CHRON16                  N2PF.                                    
      @33     CHRON17                  N2PF.                                    
      @35     CHRON18                  N2PF.                                    
      @37     CHRON19                  N2PF.                                    
      @39     CHRON20                  N2PF.                                    
      @41     CHRON21                  N2PF.                                    
      @43     CHRON22                  N2PF.                                    
      @45     CHRON23                  N2PF.                                    
      @47     CHRON24                  N2PF.                                    
      @49     CHRONB1                  N2PF.                                    
      @51     CHRONB2                  N2PF.                                    
      @53     CHRONB3                  N2PF.                                    
      @55     CHRONB4                  N2PF.                                    
      @57     CHRONB5                  N2PF.                                    
      @59     CHRONB6                  N2PF.                                    
      @61     CHRONB7                  N2PF.                                    
      @63     CHRONB8                  N2PF.                                    
      @65     CHRONB9                  N2PF.                                    
      @67     CHRONB10                 N2PF.                                    
      @69     CHRONB11                 N2PF.                                    
      @71     CHRONB12                 N2PF.                                    
      @73     CHRONB13                 N2PF.                                    
      @75     CHRONB14                 N2PF.                                    
      @77     CHRONB15                 N2PF.                                    
      @79     CHRONB16                 N2PF.                                    
      @81     CHRONB17                 N2PF.                                    
      @83     CHRONB18                 N2PF.                                    
      @85     CHRONB19                 N2PF.                                    
      @87     CHRONB20                 N2PF.                                    
      @89     CHRONB21                 N2PF.                                    
      @91     CHRONB22                 N2PF.                                    
      @93     CHRONB23                 N2PF.                                    
      @95     CHRONB24                 N2PF.                                    
      @97     DXMCCS1                  $CHAR11.                                 
      @108    DXMCCS2                  $CHAR11.                                 
      @119    DXMCCS3                  $CHAR11.                                 
      @130    DXMCCS4                  $CHAR11.                                 
      @141    DXMCCS5                  $CHAR11.                                 
      @152    DXMCCS6                  $CHAR11.                                 
      @163    DXMCCS7                  $CHAR11.                                 
      @174    DXMCCS8                  $CHAR11.                                 
      @185    DXMCCS9                  $CHAR11.                                 
      @196    DXMCCS10                 $CHAR11.                                 
      @207    DXMCCS11                 $CHAR11.                                 
      @218    DXMCCS12                 $CHAR11.                                 
      @229    DXMCCS13                 $CHAR11.                                 
      @240    DXMCCS14                 $CHAR11.                                 
      @251    DXMCCS15                 $CHAR11.                                 
      @262    DXMCCS16                 $CHAR11.                                 
      @273    DXMCCS17                 $CHAR11.                                 
      @284    DXMCCS18                 $CHAR11.                                 
      @295    DXMCCS19                 $CHAR11.                                 
      @306    DXMCCS20                 $CHAR11.                                 
      @317    DXMCCS21                 $CHAR11.                                 
      @328    DXMCCS22                 $CHAR11.                                 
      @339    DXMCCS23                 $CHAR11.                                 
      @350    DXMCCS24                 $CHAR11.                                 
      @361    E_MCCS1                  $CHAR11.                                 
      @372    E_MCCS2                  $CHAR11.                                 
      @383    E_MCCS3                  $CHAR11.                                 
      @394    E_MCCS4                  $CHAR11.                                 
      @405    E_MCCS5                  $CHAR11.                                 
      @416    E_MCCS6                  $CHAR11.                                 
      @427    E_MCCS7                  $CHAR11.                                 
      @438    E_MCCS8                  $CHAR11.                                 
      @449    INJURY                   N2PF.                                    
      @451    INJURY_CUT               N2PF.                                    
      @453    INJURY_DROWN             N2PF.                                    
      @455    INJURY_FALL              N2PF.                                    
      @457    INJURY_FIRE              N2PF.                                    
      @459    INJURY_FIREARM           N2PF.                                    
      @461    INJURY_MACHINERY         N2PF.                                    
      @463    INJURY_MVT               N2PF.                                    
      @465    INJURY_NATURE            N2PF.                                    
      @467    INJURY_POISON            N2PF.                                    
      @469    INJURY_STRUCK            N2PF.                                    
      @471    INJURY_SUFFOCATION       N2PF.                                    
      @473    INTENT_ASSAULT           N2PF.                                    
      @475    INTENT_SELF_HARM         N2PF.                                    
      @477    INTENT_UNINTENTIONAL     N2PF.                                    
      @479    KEY                      18.                                      
      @497    MULTINJURY               N2PF.                                    
      @499    PCLASS1                  N2PF.                                    
      @501    PCLASS2                  N2PF.                                    
      @503    PCLASS3                  N2PF.                                    
      @505    PCLASS4                  N2PF.                                    
      @507    PCLASS5                  N2PF.                                    
      @509    PCLASS6                  N2PF.                                    
      @511    PCLASS7                  N2PF.                                    
      @513    PCLASS8                  N2PF.                                    
      @515    PCLASS9                  N2PF.                                    
      @517    PCLASS10                 N2PF.                                    
      @519    PCLASS11                 N2PF.                                    
      @521    PCLASS12                 N2PF.                                    
      @523    PCLASS13                 N2PF.                                    
      @525    PCLASS14                 N2PF.                                    
      @527    PCLASS15                 N2PF.                                    
      @529    PCLASS16                 N2PF.                                    
      @531    PCLASS17                 N2PF.                                    
      @533    PCLASS18                 N2PF.                                    
      @535    PCLASS19                 N2PF.                                    
      @537    PRMCCS1                  $CHAR8.                                  
      @545    PRMCCS2                  $CHAR8.                                  
      @553    PRMCCS3                  $CHAR8.                                  
      @561    PRMCCS4                  $CHAR8.                                  
      @569    PRMCCS5                  $CHAR8.                                  
      @577    PRMCCS6                  $CHAR8.                                  
      @585    PRMCCS7                  $CHAR8.                                  
      @593    PRMCCS8                  $CHAR8.                                  
      @601    PRMCCS9                  $CHAR8.                                  
      @609    PRMCCS10                 $CHAR8.                                  
      @617    PRMCCS11                 $CHAR8.                                  
      @625    PRMCCS12                 $CHAR8.                                  
      @633    PRMCCS13                 $CHAR8.                                  
      @641    PRMCCS14                 $CHAR8.                                  
      @649    PRMCCS15                 $CHAR8.                                  
      @657    PRMCCS16                 $CHAR8.                                  
      @665    PRMCCS17                 $CHAR8.                                  
      @673    PRMCCS18                 $CHAR8.                                  
      @681    PRMCCS19                 $CHAR8.                                  
      @689    U_BLOOD                  N2PF.                                    
      @691    U_CATH                   N2PF.                                    
      @693    U_CCU                    N2PF.                                    
      @695    U_CHESTXRAY              N2PF.                                    
      @697    U_CTSCAN                 N2PF.                                    
      @699    U_DIALYSIS               N2PF.                                    
      @701    U_ECHO                   N2PF.                                    
      @703    U_ED                     N2PF.                                    
      @705    U_EEG                    N2PF.                                    
      @707    U_EKG                    N2PF.                                    
      @709    U_EPO                    N2PF.                                    
      @711    U_ICU                    N2PF.                                    
      @713    U_LITHOTRIPSY            N2PF.                                    
      @715    U_MHSA                   N2PF.                                    
      @717    U_MRT                    N2PF.                                    
      @719    U_NEWBN2L                N2PF.                                    
      @721    U_NEWBN3L                N2PF.                                    
      @723    U_NEWBN4L                N2PF.                                    
      @725    U_NUCMED                 N2PF.                                    
      @727    U_OBSERVATION            N2PF.                                    
      @729    U_OCCTHERAPY             N2PF.                                    
      @731    U_ORGANACQ               N2PF.                                    
      @733    U_OTHIMPLANTS            N2PF.                                    
      @735    U_PACEMAKER              N2PF.                                    
      @737    U_PHYTHERAPY             N2PF.                                    
      @739    U_RADTHERAPY             N2PF.                                    
      @741    U_RESPTHERAPY            N2PF.                                    
      @743    U_SPEECHTHERAPY          N2PF.                                    
      @745    U_STRESS                 N2PF.                                    
      @747    U_ULTRASOUND             N2PF.                                    
      ;                                                                         
                                                                                
                                                                                
RUN;

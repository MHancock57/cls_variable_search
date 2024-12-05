# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 16:46:00 2023

version5 created after meeting with AS June24
version6 edits to matc new columns names topic-> sub_topic, area-> topic, source-> survey_data_type

@author: utnvmph
"""

#   from https://www.appsloveworld.com/pandas/100/10/how-to-display-a-pandas-dataframe-as-datatable?expand_article=1   

import pandas as pd
# import numpy as np
# import json

#  first prepare the dataframe

#  select all or sample

#  


working_folder='S:/IOECLS_Data_Management/_Metadata/CLS_variable_search_tool_dev'
resources_folder=working_folder+'/resources'


df_input= pd.read_excel(resources_folder+'/metadata_datadict_all.xlsx',\
                             dtype={'research_topic_code':str, 'research_subtopic_code': str,'instrument_section':str,'instrument_subsection':str})


df_input['sweep-year-age']=df_input['cohort_name'].str.replace('bcs70','bcs').str.replace('next steps','ns').str.upper()+df_input['sweep-year-age'].str.replace('Sweep','').str.replace('cross-sweep','_cross-sweep')\
                .str.replace(r'/(\d{1,4}) ', ' ', regex=True).str.replace(' years old','y').str.replace(' months old','m').str.replace('-','_').str.replace(' ','')
df_input['study']=df_input['cohort_name'].str.replace('ncds','1958 ncds').str.replace('bcs70','1970 bcs').str.upper()
#  survey_type was originally source  now not relevant  and surcy _type is now called survey_data_type
#  df_input['survey_type']=df_input['source']


# getting a df of unique values of cohort_name and sweep
sweeps_df = df_input[['study', 'sweep', 'sweep-year-age']].drop_duplicates().sort_values(['study','sweep'])
#  need to add in -99 values for all sweeps for a cohort
all_study_sweeps_df=sweeps_df.copy().drop_duplicates(subset=['study'])
all_study_sweeps_df['sweep']=-99
all_study_sweeps_df['sweep-year-age']=' -- ALL ' + all_study_sweeps_df['study'].str.replace('1970 ','').str.replace('1958 ','').str.replace('NEXT STEPS','NS')+ ' sweeps'
#  appending the all_study_sweeps_df to sweeps_df and sorting 
sweeps_df=pd.concat([sweeps_df,all_study_sweeps_df],axis=0).sort_values(['study','sweep'])

sweeps_df.to_csv(resources_folder+'/sweep_list.csv', index=False)
# getting a df of unique values of respondent
respondent_df = df_input[~df_input['respondent'].isnull()][['respondent']].drop_duplicates().sort_values(['respondent'])
respondent_df.to_csv(resources_folder+'/respondent_list.csv', index=False)
# getting a df of unique values of about_whom
about_whom_df = df_input[~df_input['about_whom'].isnull()][['about_whom']].drop_duplicates().sort_values(['about_whom'])
about_whom_df.to_csv(resources_folder+'/about_whom_list.csv', index=False)
# getting a df of unique values of scale
scale_df = df_input[~df_input['scale'].isnull()][['scale']].drop_duplicates().sort_values(['scale'])
scale_df.to_csv(resources_folder+'/scale_list.csv', index=False)
# getting a df of unique values of survey_data_type
#  survey_data_type: strip leading and trailing blanks and set to lowercase to avoid dups 
df_input['survey_data_type']=df_input['survey_data_type'].str.strip().str.lower()
survey_data_type_df = df_input[~df_input['survey_data_type'].isnull()].sort_values(['survey_data_type'])['survey_data_type'].drop_duplicates()
survey_data_type_df.to_csv(resources_folder+'/survey_data_type_list.csv', index=False)
# getting a df of unique values of category
#  catgegory: strip leading and trailing blanks and set to lowercase to avoid dups 
df_input['category']=df_input['ukds_sn_category'].str.strip().str.lower()
category_df = df_input[~df_input['category'].isnull()].sort_values(['category'])['category'].drop_duplicates()
category_df.to_csv(resources_folder+'/category_list.csv', index=False)



#  take qnaire title from closer if missing take from cls
df_input['qnaire']=  df_input['closer_questionnaire_or_instrument']
df_input[df_input['closer_questionnaire_or_instrument']=='']['qnaire']=  df_input[df_input['closer_questionnaire_or_instrument']=='']['cls_questionnaire_or_instrument']

# computing variable type
def compute_var_type(var_spss_format):
    if (var_spss_format[:1]=='A'):
        return 'String'
    elif(var_spss_format[:1]=='F'):
        return 'Numeric'
    elif('date' in var_spss_format.lower()):
        return 'Date'
    elif('time' in var_spss_format.lower()):
        return 'Time'

df_input['var_type']=df_input.apply(lambda x: compute_var_type(x['var_spss_format']), axis=1)

# getting a df of unique values of var_type
source_df = df_input[['var_type']].drop_duplicates().sort_values(['var_type'])
source_df.to_csv(resources_folder+'/var_type_list.csv', index=False)

# print(df_input[['var_spss_format', 'var_type']][df_input['var_type']=='Date'].head(50))




#    columns are: 'cohort_name',	'category', 'sweep',	'variable_id',	'dataset_name',	'variable_name',	'variable_label',	'research_topic_code',	'research_topic',	'research_subtopic_code',	
#                'research_subtopic',	'question_number',	'question_text',	'sweep-year-age',	'survey_data_type',	'cls_questionnaire_or_instrument',	'closer_questionnaire_or_instrument',	
#                'mode',	'sweep_modes',	'questionnaire_subsection',	'scale',	'capi_code',	'respondent',	'sweep_respondents',	'about_whom',	'value_labels',	'data_sharing_licence',	
#                'ukds_deposit',	'ukds_sn',	'var_order',	'var_spss_format','var_type', 'closer_url', 'qnaire'


df_input['variable_name_plain']=df_input['variable_name'].fillna('')
df_input['variable_closer_identifier']=df_input['variable_closer_identifier'].fillna('')
df_input['qnaire']=df_input['qnaire'].fillna('')
df_input['instrument_section']=df_input['instrument_section'].fillna('')
df_input['instrument_subsection']=df_input['instrument_subsection'].fillna('')
df_input['instrument_closer_identifier']=df_input['instrument_closer_identifier'].fillna('')
df_input['instrument_closer_pdf']=df_input['instrument_closer_pdf'].fillna('')
df_input['question_number']=df_input['question_number'].fillna('')
df_input['question_text']=df_input['question_text'].fillna('')
df_input['question_closer_identifier']=df_input['question_closer_identifier'].fillna('')
df_input['derived']=df_input['derived'].fillna('No')
#  df_input['harmony_question']=df_input['question_text']
#  below not working  how to get the quesiton number included
#  df_input['harmony_question']='{question_no:"'+df_input['question_number']+'", question_text:"'+df_input['question_text']+'"}'
#  note the variable name variable label is included below in case better to use instead of question text
df_input['harmony_question']= df_input['question_number']+'||'+df_input['question_text']+'||'+df_input['qnaire']
df_input['harmony_question_vlab']= df_input['variable_name']+'||'+df_input['variable_label']+'||'+df_input['dataset_name']

#  print(df_input['harmony_question'].head())

#  computing vaiable_link below ( html link to Closer variable page)  BUT not used after meeting with AS June24
def compute_variable_link(cohort_name,variable_name,variable_closer_identifier):
    #  if no link to closer page just have name
    variable_link=variable_name
    if(variable_closer_identifier !=''):
        variable_link='<a href=https://discovery.closer.ac.uk/item/uk.cls.'+cohort_name+'/'+variable_closer_identifier+' target="_blank">'+variable_name+'</a>'
    return str(variable_link) 

df_input['variable_link']=df_input.apply(lambda x: compute_variable_link(x['cohort_name'],x[ 'variable_name_plain'],x['variable_closer_identifier']), axis=1)

def compute_qnaire_link(cohort_name,qnaire,instrument_section, instrument_subsection, instrument_closer_identifier):
    #  if no link to closer page just have name
    qnaire_text=qnaire
    if(instrument_section !='') :
       qnaire_text += '     '+instrument_section
       if(instrument_subsection !=''):
           qnaire_text += '     '+instrument_subsection
    qnaire_link=qnaire_text
    if(instrument_closer_identifier !=''):
        qnaire_link='<a href=https://discovery.closer.ac.uk/item/uk.cls.'+cohort_name+'/'+instrument_closer_identifier+' target="_blank">'+qnaire_text+'</a>'
    return str(qnaire_link)

df_input['qnaire_link']=df_input.apply(lambda x: compute_qnaire_link(x['cohort_name'],x[ 'qnaire'],x['instrument_section'],x['instrument_subsection'],x['instrument_closer_identifier']), axis=1)

def compute_question_link(cohort_name,question_number,question_text ,question_closer_identifier):
    #  if no link to closer page just have name
    question_link=question_number+'       : ' + question_text
    if(question_closer_identifier !=''):
        question_link='<a href=https://discovery.closer.ac.uk/item/uk.cls.'+cohort_name+'/'+question_closer_identifier+' target="_blank">'+question_number+'       : ' + question_text+'</a>'
    return str(question_link)
df_input['question_link']=df_input.apply(lambda x: compute_question_link(x['cohort_name'],x[ 'question_number'], x[ 'question_text'],x['question_closer_identifier']), axis=1)



def compute_pdf_link(instrument_closer_pdf, qnaire):
    pdf_link=''
    if(instrument_closer_pdf !=''):
        pdf_link='<a href='+instrument_closer_pdf+' target="_blank"> '+qnaire +'</a>'
    return str(pdf_link)
df_input['instrument_closer_pdf_link']=df_input.apply(lambda x: compute_pdf_link(x['instrument_closer_pdf'],x[ 'qnaire']), axis=1)



#  in computing more_info below some edtiing after meeting with AS June 24
#  line above was + df_input['variable_link but not including link to closer variable page after meeting with AS June24']
# '<br /><b>Question: </b>'+ df_input['qnaire_link']+'      : '+df_input['question_link']+\

df_input['more_info']='<b>Variable: </b>'+ df_input['variable_name']+\
                '<br /><b>Instrument: </b>'+ df_input['qnaire'] + '<b>       Section: </b>' + df_input['instrument_section'] +\
                '<br /><b>Instrument PDF: </b>'+df_input['instrument_closer_pdf_link'] +\
                '<br /><b>Question: </b>'+  df_input['question_link']+\
                '<br /><b>Respondent / About whom : </b>'+ df_input['respondent'].fillna('')+'      : ' + df_input['about_whom'].fillna('')+\
                '<br /><b>Value labels: </b>'+df_input['value_labels'].fillna('').str.replace('(','\n(', regex=False)+\
                '<br /><b>Scale: </b>  '+ df_input['scale'].fillna('')+\
                '<br /><b>Value Type: </b>'+ df_input['var_type'].fillna('')+'     : ' + df_input['var_spss_format'].fillna('')
                
                
            
#  combining reseach topic and subtopic
def compute_research_topic_subtopic(topic,subtopic):
    if str(topic).strip() != str(subtopic).strip():
        return str(topic)+':'+str(subtopic)
    else:
        return str(topic) 
df_input['research_topic_subtopic']=df_input.apply(lambda x: compute_research_topic_subtopic(x['research_topic'],x[ 'research_subtopic']), axis=1)
#  combining data sharing livce and sn
def compute_UKDS_licence_sn(licence,sn):
    return str(licence)+': SN'+str(sn)
df_input['UKDS_SN']=df_input.apply(lambda x: compute_UKDS_licence_sn(x['data_sharing_licence'],x[ 'ukds_sn']), axis=1)

#  commenting out below as not using the closer variable link in the CLS metadata searc search 
# df_input['variable_name']=df_input['variable_link']

df_input['click_col']=''
df_input['child_row']=''

df_input['dataset_name']=df_input['dataset_name'].str.replace('.sav','', regex=False)

#  'research_subtopic_code'  is added for the selectionprocess but not shown in datatables

df=df_input[['child_row', 'study', 'category', 'research_topic_subtopic','sweep-year-age', 'variable_name','variable_label', 'survey_data_type','derived',	\
             'UKDS_SN', 'dataset_name',	'harmony_question','harmony_question_vlab', 'more_info', 'click_col','research_topic_code','research_subtopic_code','respondent','about_whom','scale','var_type' ,'capi_code',]]

#  renaming columns to match html file

df=df.rename(columns={'research_topic_code':'topic_code','research_subtopic_code':'subtopic_code'})

#  adding blanks  to force  the variable label column in datatable wider?
# df=df.rename(columns={"variable_label":"variable_label                                       ","UKDS_SN":"UKDS_SN    ","sweep-year-age":"sweep-year-age      ","research_topic_subtopic": "research_topic_subtopic                                "})

# df.to_excel(r'S:\IOECLS_Data_Management\_Metadata\MH_working\pandas_to_datatables\df_for_datatables.xlsx', index=False)
#  df.to_csv(resources_folder+'/df_for_datatables_sample.csv', index=False)

df.to_csv(resources_folder+'/metadata_datatables.csv', index=False)




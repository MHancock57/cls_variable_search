# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 16:46:00 2023

version24 toedit column names area, topic, ssource -> topic, subtopic, survey_data_type
version25 including harmony again (just for mental health topic variables?)  including the variable lable harmony link?

@author: utnvmph
"""

#   from https://www.appsloveworld.com/pandas/100/10/how-to-display-a-pandas-dataframe-as-datatable?expand_article=1   

from flask import Flask, render_template, request, jsonify, send_file, make_response
import pandas as pd
import numpy as np
import json

#  the csv file for the DF is created in python script flask_datatables_csv_create.py

# Initialize the Flask application
# app = Flask(__name__)

working_folder='S:\IOECLS_Data_Management\_Metadata\CLS_variable_search_tool_dev'
app = Flask(__name__, template_folder=working_folder+'/templates')

resources_folder=working_folder+'/resources'


@app.route('/')
def index():
    variable_type=['string','integer']
    #  reading in the excel files for the drop down selection list
    subtopic_list = pd.read_excel(resources_folder+'/topic_list.xlsx').to_dict(orient='records')
    # topic-list of the 3 character subtopic codes (i.e. research topics)
    subtopic_df=pd.read_excel(resources_folder+'/topic_list.xlsx', dtype={'value':str})
    subtopic_df['label']=subtopic_df['label'].str.replace(' - other','')
    topic_list=subtopic_df[subtopic_df['value'].str.len()==3].to_dict(orient='records')
    #   sweep_df=pd.read_csv(resources_folder+'/sweep_list.csv')
    category_list = pd.read_csv(resources_folder+'/category_list.csv').to_dict(orient='records')
    sweep_list = pd.read_csv(resources_folder+'/sweep_list.csv').to_dict(orient='records')
    study_df=pd.read_csv(resources_folder+'/sweep_list.csv')[['study','sweep']].drop_duplicates(subset=['study'])
    study_df['sweep']=99
    study_list=study_df.to_dict(orient='records')
    respondent_list = pd.read_csv(resources_folder+'/respondent_list.csv').to_dict(orient='records')
    about_whom_list = pd.read_csv(resources_folder+'/about_whom_list.csv').to_dict(orient='records')
    scale_list = pd.read_csv(resources_folder+'/scale_list.csv').to_dict(orient='records')
    survey_data_type_list = pd.read_csv(resources_folder+'/survey_data_type_list.csv').to_dict(orient='records')
    var_type_list = pd.read_csv(resources_folder+'/var_type_list.csv').to_dict(orient='records')
    return render_template('cls_variable_search_index.html', variable_type=variable_type, category_list=category_list, topic_list=topic_list, subtopic_list=subtopic_list, study_list=study_list, sweep_list= sweep_list , \
                                                        respondent_list=respondent_list,about_whom_list=about_whom_list,scale_list=scale_list, survey_data_type_list=survey_data_type_list,var_type_list = var_type_list )


@app.route('/get_metadata')
def metadata():
    return send_file(resources_folder+'/metadata_datadict_all.xlsx', as_attachment=True)


@app.route('/about')
def about():
    return render_template('cls_variable_search_about.html')


@app.route('/_get_table')
def get_table():
    # cohort_name = request.args.get('cohort_name', type=str)
    #  converting the json string in filter_values to a python list of dictionaries

    filter_values = json.loads(request.args.get('filter_values'))
    # convert the list of dictionaries {name:value} to a dictionary with keys and strings (that look like lists) as values
    #             {['name1':['value1','value2' ], ['name2':['value1','value2'...'valuen'] }


    # if area_code and topic code are both included then need to be joined by or so separate out into another dict (topic_filter_dict)
    filter_dict={}
    topic_filter_dict={}
    study_sweep_filter_dict={}
    #  if survey_data_type included then needs to apply only if category =survey or sub-study
    survey_data_type_filter_dict={}
    study_lookup_dict={'NC':'1958 NCDS', 'BC':'1970 BCS', 'MC':'MCS','NS': 'NEXT STEPS' }
    for dict in filter_values:
        if(dict["name"] in ['topic_code']):           
            dict_name=dict["name"]
            dict_value=dict["value"]
            #  if there is a 99 in subtopic_code then should be topic_code without the 99
            if(dict_name=='topic_code' and dict_value[-2:]=='99' ):
                dict_value=dict_value[:3]
            else:
                dict_name='subtopic_code' 
            if(dict_name in topic_filter_dict):
                topic_filter_dict[dict_name]+=',"'+dict_value+'"'
            else:
                topic_filter_dict[dict_name]='"'+dict_value+'"'
                
        elif(dict["name"] in ['study_sweep']):           
            dict_name=dict["name"]
            dict_value=dict["value"]
            #  if value starts with ' -- ALL' then dict_name name should be study fro mchars 8-10 and lookup
            print('dict_name dict_value ', dict_name, dict_value)
            if(dict_name=='study_sweep' and dict_value[:7]==' -- ALL' ):
                dict_name='study'
                print('inside ***', dict_value[8:10])
                dict_value=study_lookup_dict[dict_value[8:10]]
                

            else:
                dict_name='sweep-year-age'
            if(dict_name in study_sweep_filter_dict):
                study_sweep_filter_dict[dict_name]+=',"'+dict_value+'"'
            else:
                study_sweep_filter_dict[dict_name]='"'+dict_value+'"'                

        elif(dict["name"] in ['survey_data_type']):           
            if(dict["name"] in survey_data_type_filter_dict):
                survey_data_type_filter_dict[dict["name"]]+=',"'+dict["value"]+'"'
            else:
                survey_data_type_filter_dict[dict["name"]]='"'+dict["value"]+'"'
                
        else:
            if(dict["name"] in filter_dict):
                filter_dict[dict["name"]]+=',"'+dict["value"]+'"'
            else:
                filter_dict[dict["name"]]='"'+dict["value"]+'"'    
     
    df_subset_str='df['
    n=0
    tot_dict_len=0    
    # if(tot_dict_len>0):
    for k,v in filter_dict.items():
        if(n==0):
            df_subset_str+=' (df["'+k+'"].isin( ['+v+']))'
            n=1
        else:
            df_subset_str+='& (df["'+k+'"].isin( ['+v+']))'
    tot_dict_len+= len(filter_dict)           
    #  adding in the survey_data_type filter
    print(survey_data_type_filter_dict)
    if(len(survey_data_type_filter_dict)>0):
        if(tot_dict_len>0):
            df_subset_str+=' & '
        n=0
        for k,v in survey_data_type_filter_dict.items():
            if(n==0):
                df_subset_str+='( (df["'+k+'"].isin( ['+v+'] ) | ~df["category"].isin( ["survey","substudy"] ))'
                n=1
            else:
                n+=1
                df_subset_str+='| (df["'+k+'"].isin( ['+v+'] ) | ~df["category"].isin( ["survey","substudy"])) )'
        if(n==1):  
            df_subset_str+=')'                  
            tot_dict_len+= len(survey_data_type_filter_dict)                  
    #  adding in the topic and subtopic code filter
    print(study_sweep_filter_dict)
    if(len(topic_filter_dict)>0 ):
        if(tot_dict_len>0):
            df_subset_str+=' & '
        n=0
        for k,v in topic_filter_dict.items():
            if(n==0):
                df_subset_str+='( (df["'+k+'"].isin( ['+v+']))'
                n=1
            else:
                n+=1
                df_subset_str+='| (df["'+k+'"].isin( ['+v+'])) )'
        if(n==1):  
            df_subset_str+=')'                  
        tot_dict_len+= len(topic_filter_dict)     
            

            
    #  adding in the study and sweep code filter            
    if(len(study_sweep_filter_dict)>0):
        if(tot_dict_len>0):
            df_subset_str+=' & '
        n=0
        for k,v in study_sweep_filter_dict.items():
            if(n==0):
                print('n=0')
                df_subset_str+='( (df["'+k+'"].isin( ['+v+']))'
                n=1
                print(n)
            else:
                print ('n!=0')
                n+=1
                df_subset_str+='| (df["'+k+'"].isin( ['+v+'])) )'
                print(n)
        if(n==1):  
            df_subset_str+=')' 
                  
        tot_dict_len+= len(study_sweep_filter_dict)            
            
            
    df_subset_str+=']'


    df=pd.read_csv(resources_folder+'/metadata_datatables.csv', \
                            dtype={'category':str,'topic_code':str,'subtopic_code':str,'respondent':str,'about_whom':str,'scale':str,'survey_data_type':str,'var_type':str})
    # df_subset_str1='df[df["cohort_name"]=="'+cohort_name+'"]'
    # df_subset_str1='df[ df["cohort_name"].isin(["ncds","mcs"])]'
    
    df1=eval(df_subset_str)
    df1=df1.drop(['topic_code','subtopic_code','respondent','about_whom','scale','var_type' ], axis=1)


    #  NOTE if Harmony buttone are to be included can sen only first 23000 rows of df1
    return jsonify( my_table=json.loads(df1.to_json(orient="split"))["data"],
                   columns=[{"title": str(col)} for col in json.loads(df1.to_json(orient="split"))["columns"]])



#  below had syntax debug=True but would not run so edited to debug=False
#  should get response      Running on http://127.0.0.1:5000  then type http://127.0.0.1:5000/ into webpage

if __name__ == '__main__':
    app.run(debug=False)    #  , port=8000
    




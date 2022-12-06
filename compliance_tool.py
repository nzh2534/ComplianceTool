# importing required modules
import PyPDF2
import re
import pandas as pd

import gspread
from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials

from sub_header_fxn import sub_header_fxn

def compliance_tool(file_path):
    creds_json = "googlesheets.json"
    sheet_name = "Compliance Tool"
    spreadsheet_id = "1Rcpj_myqpIDSQDIfJZX0uDbTxMxrhP0hhvkepTeG0p4"
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json,scope)
    client = gspread.authorize(creds)
    
    # creating a pdf file object
    pdfFileObj = open(file_path, 'rb')
    
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    
    # Makes a list of all pages
    first_page = 0
    final_page = pdfReader.numPages
    page_list = ["blank"]
    while first_page < final_page:
        page_list.append(pdfReader.getPage(first_page).extractText().lower())
        first_page += 1

    #Finds ToC
    toc_regex = r"table\s+of\s+contents"
    for page in page_list[:5]:
        if re.search(toc_regex, page, re.MULTILINE | re.IGNORECASE):
            toc_page = page_list.index(page)
            break
        else:
            toc_page = 3

    #Makes ToC list into sections from NOFO, removes spaces surrounding each
    toc_page = page_list[toc_page].split("\n")

    for line in toc_page:
        if re.search(toc_regex, line, re.MULTILINE | re.IGNORECASE):
            last_line = toc_page.index(line)
        else:
            last_line = -1

    toc_page = toc_page[last_line + 1:]

    final_contents = []

    for line in toc_page:
        if re.search(r"[a-z]", line, re.MULTILINE | re.IGNORECASE):
            final_contents.append(line.strip())
        
    #Identifies section and their pages, putting section (key) with pages (value;list) into dict
    contents_dict = {}
    section_pages = []

    for section in final_contents:
        if re.search(r"[0-9]+$", section, re.MULTILINE | re.IGNORECASE):
            section_pages.append(int(re.search(r"[0-9]+$", section, re.MULTILINE | re.IGNORECASE).group()))
            contents_dict[section] = int(re.search(r"[0-9]+$", section, re.MULTILINE | re.IGNORECASE).group())

    #Adds 1 to the final page so it doesn't get reduced too much
    section_pages.append(final_page + 1)

    index = 0
    for key in contents_dict:
        contents_dict[key] = [contents_dict[key],section_pages[index + 1] - 1]
        index += 1

    #Assigning page start and ends for Federal Award Information, Eligibility, and Submission Info
    for key in contents_dict:
        if re.search(r"a(\s+)?w(\s+)?a(\s+)?r(\s+)?d(\s+)?i(\s+)?n(\s+)?f(\s+)?o(\s+)?r(\s+)?m(\s+)?a(\s+)?t(\s+)?i(\s+)?o(\s+)?n|i(\s+)?n(\s+)?f(\s+)?o(\s+)?r(\s+)?m(\s+)?a(\s+)?t(\s+)?i(\s+)?o(\s+)?n(\s+)?(\s+)?o(\s+)?f(\s+)?f(\s+)?e(\s+)?d(\s+)?e(\s+)?r(\s+)?a(\s+)?l(\s+)?a(\s+)?w(\s+)?a(\s+)?r(\s+)?d", key, re.MULTILINE | re.IGNORECASE):
            info_page_one = contents_dict[key][0]
            info_page_end = contents_dict[key][1]
        if re.search(r"e(\s+)?l(\s+)?i(\s+)?g(\s+)?i(\s+)?b(\s+)?i(\s+)?l(\s+)?i(\s+)?t(\s+)?y", key, re.MULTILINE | re.IGNORECASE):
            elig_page_one = contents_dict[key][0]
            elig_page_end = contents_dict[key][1]
        if re.search(r"s(\s+)?u(\s+)?b(\s+)?m(\s+)?i(\s+)?s(\s+)?s(\s+)?i(\s+)?o(\s+)?n", key, re.MULTILINE | re.IGNORECASE):
            subm_page_one = contents_dict[key][0]
            subm_page_end = contents_dict[key][1]

    def page_scraper(first,end,page_list):
        x = []
        while first != end + 1:
            x.append(page_list[first])
            first += 1
        return x

    fed_award_info = "\n".join(page_scraper(info_page_one,info_page_end,page_list))
    elig_info = "\n".join(page_scraper(elig_page_one,elig_page_end,page_list))
    subm_info = "\n".join(page_scraper(subm_page_one,subm_page_end,page_list))

    def header_extractor(pages,fxn,type_var): #type is for sub headers (s) (EX: 1. or A.1) or sub sub headers (EX: a) or (1) (ss) )
        list_numbering = []
        list_names = []

        #r"^(\s+)?[0-9]+\..+" ------- For 1. headers
        #r"^(\s+)?[a-z]\.[0-9]+.+" ----- For A.1 headers
        if type_var == "s":
            for match in re.finditer(r"^(^(\s+)?[0-9]+\..+)|(^(\s+)?[a-z]\.[0-9]+.+)", pages, re.MULTILINE | re.IGNORECASE):
                match_int = match.group().strip().split(" ")[0].replace('.','',1)
                for i in match_int:
                    if re.search(r"[a-z]", match_int, re.MULTILINE | re.IGNORECASE):
                        match_int = match_int.replace(i,"")
                try:
                    list_numbering.append(float(match_int))
                except ValueError:
                    continue
                list_names.append(match.group().strip())
        else:
            for match in re.finditer(r"(^(\s+)?[a-hj-uw-z]\..+)|(^(\s+)?\([0-9]+\).+)|(^(\s+)?[0-9]+\..+)|(^(\s+)?[a-z]\.[0-9]+.+)|(^(\s+)?[a-z]\).+)", pages, re.MULTILINE | re.IGNORECASE):
                list_names.append(match.group().strip())


        print(list_numbering)
        print(list_names)

        primary_header_names = []

        if type_var == "s":
            primary_headers_index = fxn(list_numbering)
            for i in primary_headers_index:
                primary_header_names.append(list_names[i])
        else:
            primary_header_names = list_names

        final_dict = {}
        final_list = []

        for i in primary_header_names:
            final_list.append([pages.index(i)])
        
        index = 1
        for i in final_list:
            if index < len(final_list):
                i.append(pages.index(primary_header_names[index]))
                index += 1
            else:
                break
        
        index = 0
        for i in primary_header_names:
            if len(final_list[index]) == 2:
                final_dict[i] = pages[final_list[index][0]:final_list[index][1]]
                index += 1
            else:
                final_dict[i] = pages[final_list[index][0]:]
                break

        return final_dict

    def post_and_refine(fxn,text,tab_name,full_page_list,type_var):
        df = pd.DataFrame(fxn(text,sub_header_fxn,type_var),index=[0]).transpose()
        df = df.rename({0: 'Details'}, axis='columns')

        page_list = []
        for i in df.index:
            page_number = "N/A"
            for page in full_page_list:
                try:
                    if re.search(i, page, re.MULTILINE | re.IGNORECASE):
                        page_number = full_page_list.index(page)
                except re.error:
                    continue
            page_list.append(page_number)

        df["Pages"] = page_list
        df["Team Member(s) Responsible"] = ""
        df["Type"] = tab_name

        #d2g.upload(df, spreadsheet_id, tab_name, credentials=creds, row_names=True)
        return df

    #For overview page
    overview_list = page_list[1].strip().split("\n")
    new_overview_list = []

    for i in overview_list:
        new_overview_list.append(i.split(":",1))

    for i in new_overview_list:
        if len(i) < 2:
            new_overview_list.remove(i) 

    for i in new_overview_list:
        if len(i) > 1:
            if re.search(r"\s+notice\s+of\s+funding", i[1], re.MULTILINE | re.IGNORECASE):
                final_overview_index = new_overview_list.index(i) + 1
                break

    new_overview_list = new_overview_list[:final_overview_index]

    overview_dict = {}
    for i in new_overview_list:
        if len(i) > 1:
            overview_dict[i[0].strip()] = i[1].strip()

    df_overview = pd.DataFrame(overview_dict,index=[0]).transpose()
    df_overview = df_overview.rename({0: 'Details'}, axis='columns')
    df_overview["Pages"] = 1
    df_overview["Team Member(s) Responsible"] = ""
    df_overview["Type"] = "Overview"

    df_fed_info = post_and_refine(header_extractor,fed_award_info,'Federal Award Information',page_list,"s")
    df_elig = post_and_refine(header_extractor,elig_info,'Eligibility Information',page_list,"s")
    df_subm = post_and_refine(header_extractor,subm_info,'Application & Submission Information',page_list,"s")

    final_df = pd.concat([df_overview,df_fed_info,df_elig,df_subm])

    for i in df_subm["Details"]:
        if re.search(r"(\s+)?t(\s+)?e(\s+)?c(\s+)?h(\s+)?n(\s+)?i(\s+)?c(\s+)?a(\s+)?l(\s+)?a(\s+)?p(\s+)?p(\s+)?l(\s+)?i(\s+)?c(\s+)?a(\s+)?t(\s+)?i(\s+)?o(\s+)?n(\s+)?f(\s+)?o(\s+)?r(\s+)?m(\s+)?a(\s+)?t", i, re.MULTILINE | re.IGNORECASE):
            df_tech = post_and_refine(header_extractor, i,"Technical Application Details",page_list,"ss")
            tech_test = final_df.index[final_df["Details"] == i]
        if re.search(r"b(\s+)?u(\s+)?s(\s+)?i(\s+)?n(\s+)?e(\s+)?s(\s+)?s.+a(\s+)?p(\s+)?p(\s+)?l(\s+)?i(\s+)?c(\s+)?a(\s+)?t(\s+)?i(\s+)?o(\s+)?n(\s+)?f(\s+)?o(\s+)?r(\s+)?m(\s+)?a(\s+)?t", i, re.MULTILINE | re.IGNORECASE):
            df_busin = post_and_refine(header_extractor, i,"Business Application Details",page_list,"ss")
            busin_test = final_df.index[final_df["Details"] == i]


    final_df = final_df.drop(tech_test)
    final_df = pd.concat([final_df,df_tech])
    
    if (tech_test == busin_test) == False:
        final_df = final_df.drop(busin_test)
        final_df = pd.concat([final_df,df_busin])

    clean_details = []
    for i in final_df["Details"]:
        clean_details.append(i.replace(final_df.index[final_df["Details"] == i].tolist()[0],"").strip())

    final_df["Details"] = clean_details

    d2g.upload(final_df, spreadsheet_id, 'Overview', credentials=creds, row_names=True)




#compliance_tool("nofo3.pdf")


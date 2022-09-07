import warnings; warnings.filterwarnings("ignore")
from tqdm import tqdm
import pandas as pd
import requests
import bs4
# =============================================================================================== #
ncbi_link = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id="
# =============================================================================================== #
genelist_link = "https://www.genenames.org/cgi-bin/download/custom?col=gd_app_sym&col=md_eg_id&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&limit=2000&order_by=gd_app_sym_sort&format=text&submit=submit"
# genelist_link = "https://www.genenames.org/cgi-bin/download/custom?col=gd_app_sym&col=md_eg_id&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit"
# =============================================================================================== #
df_genelist = pd.read_csv(genelist_link, header=0, sep="\t", error_bad_lines=False)
# =============================================================================================== #
genelist = df_genelist['NCBI Gene ID(supplied by NCBI)'].fillna(0).astype(int).tolist()
genelist = [x for x in genelist if str(x) != 'nan']
genelist = [x for x in genelist if str(x) != '0']
# print(genelist)
# =============================================================================================== #
bs_data  = []
bs_error = []
# =============================================================================================== #
for i in tqdm(genelist, desc='Progress: '):
    try:
        url_link = str(ncbi_link + str(i))
        r = requests.get(url_link)
        soup = bs4.BeautifulSoup(r.content, 'xml')
        name_bs = soup.find("Name").text
        description_bs = soup.find("Description").text
        species_bs = soup.find("ScientificName").text
        aliases_bs = soup.find("OtherAliases").text
        summary_bs = soup.find("Summary").text
        #print(i, '\t\t\t', name_bs, '\t\t\t', species_bs, '\t\t\t', description_bs)
        bs_data.append({'UID': i, 'ScientificName': species_bs, 'Description': description_bs,
                        'Name': name_bs, 'Summary': summary_bs})

    except AttributeError:
        bs_error.append({'UID': i, 'Error': 'Error'})
        bs_data.append({'UID': i, 'ScientificName': "Error", 'Description': "Error",
                        'Name': "Error",'Summary': "Error"})
# =============================================================================================== #
df_bs = pd.DataFrame(data=bs_data, columns=['UID','ScientificName','Name','Description','Summary'])
df_bs.rename(columns={'Name':'GeneSymbol','Summary':'GeneSummary'}, inplace=True)
df_error = pd.DataFrame(data=bs_error, columns=['UID','Error'])
# =============================================================================================== #
df_bs.to_csv('./OutputData/NCBI_Eutils_v03_output.csv',      index=False, sep='\t')
df_error.to_csv('./OutputData/NCBI_Eutils_v03_errorlog.csv', index=False, sep='\t')
# =============================================================================================== #
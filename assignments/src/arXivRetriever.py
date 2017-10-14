"""
A python program to create and store coauthorship graphs of publised ArXiv papers.
Author: Sailik Sengupta
"""

from graph_tool.all import *
from pylab import *
import arxivscraper
import matplotlib
import datetime
import pandas
import sys

def plot_degrees(graph, date_from):
    hist = vertex_hist(graph, deg="total")
    errorbar(hist[1][:-1], hist[0], fmt="o", label="total")
    xlabel("Vertex (author) number")
    ylabel("Co-authors")
    tight_layout()
    savefig("{}.pdf".format(date_from))
    savefig("{}.png".format(date_from)) 

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print("Please execute:\n python <codefile>.py <category_name> <start_date>")
        exit(1)

    # Set inputs for retrieving arXiv records
    category = sys.argv[1]
    date_from = sys.argv[2]
    date_until = str(datetime.date.today())

    graph_name = "graph_{}_{}.xml.gz".format(category, date_from)
    co_auth_graph = Graph(directed=False)
    try:
        co_auth_graph.load(graph_name)
    except:
        print("[DEBUG] Graph data does not exist. Scraping ArXiv!")
        # Retrieve the records
        scraper = arxivscraper.Scraper(category=category, date_from=date_from,date_until=date_until)
        output = scraper.scrape()

        # Store it in a panda dataframe
        cols = ('id', 'title', 'categories', 'abstract', 'doi', 'created', 'updated', 'authors')
        df = pandas.DataFrame(output, columns=cols)

        # Create an adj list for authorship
        co_auth_adj_list = {}
        for author_list in df['authors']:
            for u in author_list:
                for v in author_list:
                    if not u == v:
                        try:
                            co_auth_adj_list[u].append(v)
                        except:
                            co_auth_adj_list[u] = []
        
        # Create co-authorship graph
        auth_vtx = {}
        for a in co_auth_adj_list.keys():
            v = co_auth_graph.add_vertex()
            auth_vtx[a] = v
        
        for a in co_auth_adj_list.keys():
            for b in co_auth_adj_list[a]:
                co_auth_graph.add_edge(auth_vtx[a], auth_vtx[b])

        co_auth_graph.save(graph_name)
        print("[DEBUG] Saved graph- {}".format(graph_name))
    
    try:
        plot_degrees(co_auth_graph, date_from)
        print("[SUCCESS] Successfully created the histogram!")
    except:
        print("[FAILED] Creating the histogram failed!")

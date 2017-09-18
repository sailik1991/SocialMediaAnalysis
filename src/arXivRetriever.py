from graph_tool.all import *
import arxivscraper
import datetime
import pandas
import sys

def plot_degrees(graph, date_from):
	hist = vertex_hist(graph, deg="total")
	#y = hist[0]
	#err = sqrt(hist[0])
	#err[err >= y] = y[err >= y] - 1e-2

	figure(figsize=(6,4))
	#errorbar(in_hist[1][:-1], in_hist[0], fmt="o", yerr=err,
	#		label="in")
	#gca().set_yscale("log")
	#gca().set_xscale("log")
	#gca().set_ylim(1e-1, 1e5)
	#gca().set_xlim(0.8, 1e3)
	#subplots_adjust(left=0.2, bottom=0.2)
	xlabel("# of people")
	ylabel("Co-author counts")
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
    co_auth_graph = Graph(directed=False)
    auth_vtx = {}
    for a in co_auth_adj_list.keys():
        v = co_auth_graph.add_vertex()
        auth_vtx[a] = v
    
    for a in co_auth_adj_list.keys():
        for b in co_auth_adj_list[a]:
            co_auth_graph.add_edge(auth_vtx[a], auth_vtx[b])

    co_auth_graph.save("graph_{}.xml.gz".format(date_from))
    graph_draw(co_auth_graph, sfdp_layour(g), output_size=(1000, 1000), vertex_color=[1,1,1,0], vertex_size=1, edge_pen_width=1.2, vcmap=matplotlib.cm.gist_heat_r, output="graph_{}.png".format(date_from) )
    plot_degrees(co_auth_graph, date_from)

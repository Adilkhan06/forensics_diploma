import networkx as nx
import plotly.graph_objects as go
from django.shortcuts import render
from analysis.models import Match


def visualize_graph(request):
    G = nx.Graph()

    matches = Match.objects.select_related('source_file', 'target_file').all()

    for match in matches:
        source_id = f"File_{match.source_file.id}"
        target_id = f"File_{match.target_file.id}"

        source_label = f"{match.source_file.file_type} {match.source_file.id}"
        target_label = f"{match.target_file.file_type} {match.target_file.id}"

        G.add_node(source_id, label=source_label)
        G.add_node(target_id, label=target_label)
        G.add_edge(source_id, target_id, weight=match.similarity_score * 10)

    pos = nx.spring_layout(G, seed=42)

    edge_trace = go.Scatter(
        x=[], y=[], line=dict(width=0.5, color='#888'),
        hoverinfo='none', mode='lines')

    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[], y=[], text=[], mode='markers+text',
        hoverinfo='text', textposition="bottom center",
        marker=dict(showscale=True, colorscale='YlGnBu', size=10,
                    color=[], colorbar=dict(thickness=15, title='Node Connections')))

    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_info = node[1].get('label', node[0])
        node_trace['text'] += tuple([node_info])

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Граф связей между файлами',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    graph_html = fig.to_html(full_html=False)

    return render(request, 'visualization/graph.html', {'graph': graph_html})
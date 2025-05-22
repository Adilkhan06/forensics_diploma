from django.shortcuts import render
from django.http import HttpResponse
from analysis.models import Match, AnalysisSession
import datetime
import pdfkit
from django.conf import settings
from analysis.utils.gemini_client import get_gemini_summary
from analysis.utils.matcher import collect_analysis_data


def generate_ai_report(request):
    raw_data = collect_analysis_data()
    ai_report = get_gemini_summary(raw_data)

    context = {
        "ai_report": ai_report,
        "raw_data": raw_data
    }

    return render(request, "reporting/ai_report.html", context)




def generate_report(request):
    config = pdfkit.configuration(wkhtmltopdf=settings.PDFKIT_CONFIG['wkhtmltopdf'])

    latest_session = AnalysisSession.objects.order_by('-started_at').first()
    if latest_session:
        matches = Match.objects.filter(session=latest_session).select_related('source_file', 'target_file')
    else:
        matches = []

    graph_html = visualize_graph_html()

    raw_data = collect_analysis_data()
    ai_report = get_gemini_summary(raw_data)

    context = {
        'matches': matches,
        'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        'graph': graph_html,
        'ai_report': ai_report
    }

    html_content = render(request, 'reporting/report_template.html', context).content.decode('utf-8')

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }

    pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="digital_forensics_report.pdf"'
    return response


def visualize_graph_html():
    from analysis.models import AnalysisSession, Match

    latest_session = AnalysisSession.objects.order_by('-started_at').first()

    if not latest_session:
        return "<p>Нет данных для построения графа</p>"

    matches = Match.objects.filter(session=latest_session).select_related('source_file', 'target_file')

    import plotly.graph_objects as go
    import networkx as nx

    G = nx.Graph()

    for match in matches:
        source_label = str(match.source_file)
        target_label = str(match.target_file)

        G.add_node(source_label, label=source_label)
        G.add_node(target_label, label=target_label)
        G.add_edge(source_label, target_label, weight=match.similarity_score * 10)

    pos = nx.spring_layout(G, seed=42)

    edge_trace = go.Scatter(
        x=[], y=[], line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

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
        node_trace['text'] += tuple([node[0]])

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Граф связей между файлами',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    return fig.to_html(full_html=False)


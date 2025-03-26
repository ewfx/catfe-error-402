import re

def segregate_links(links):
    """Segregate links into Confluence, JIRA, and Other categories."""
    confluence_links = []
    jira_links = []
    other_links = []

    # Define patterns for Confluence and JIRA links
    confluence_pattern = r'(:?https?://)?[^\s]+/wiki/[^\s]*'
    jira_pattern = r'(:?https?://)?[^\s]+/browse/[^\s]*'

    for link in links:
        if re.match(confluence_pattern, link):
            confluence_links.append(link)
        elif re.match(jira_pattern, link):
            jira_links.append(link)
        else:
            other_links.append(link)

    return {
        "confluence_links": confluence_links,
        "jira_links": jira_links,
        "other_links": other_links
    }

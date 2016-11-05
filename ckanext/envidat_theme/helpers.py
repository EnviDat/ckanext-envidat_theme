from ckanext.hierarchy import helpers
import ckan.plugins as p

# Copied from hierarchy, maybe this code should go there!!
def envidat_theme_get_children_packages(organization, count=2):

    def _children_name_list(children):
        name_list = []
        for child in children:
            name = child.get('name', "")
            name_list += [name] + _children_name_list(child.get('children', []))
        return name_list

    packages = organization.get('packages', [])
    children_organizations = _children_name_list(helpers.group_tree_section(organization['id'], include_parents=False, include_siblings=False).get('children',[]))
    for children in children_organizations:
        packages += p.toolkit.get_action('organization_show')({},{'id':children, 'include_datasets':True}).get('packages', [])
    return packages[:count]


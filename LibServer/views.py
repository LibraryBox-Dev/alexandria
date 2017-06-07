"""
BoxNG admin panel.
"""

from datetime import datetime
from flask import render_template, abort, redirect
from LibServer import app

from configparser import ConfigParser

#
# This is the simplest route in the entire app.
# All this does is show some details about what's turned on and what
# isn't. 
#

@app.route('/')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
    )


# Configuration sections

configuration_groups = {
    "general":{
        "name":"General configuration",
        "short":"General",
        "desc":"Overall configuration of your box",
        "icon":"fa fa-cog",
        "section":"general",
        "type":"single",
        "template":"cfg_general.html"
        },
    "network": {
        "name":"Network (general)",
        "short":"Network",
        "desc":"Configure DNS and other general network configuration",
        "icon":"fa fa-wrench",
        "type":"multi",
        "template":"cfg_network.html",
        "section":"network",
        "namespace":"interface",
        "leaf":"Network"
        },
#    "network_interface":{
#        "name":"Interface Configuration",
#        "short":"Network Interfaces",
#        "desc":"Configure how your box uses its network interfaces",
#        "icon":"fa fa-microchip",
#        "namespace": "interface",
#        "type":"multi",
#        "template":None,
#        "leaf":"Interface"
#        },
    "services":{
        "name":"Service Configuration",
        "short":"Services",
        "desc":"Services you can run on your box",
        "icon":"fa fa-server",
        "namespace":"service",
        "type":"multi",
        "template":"cfg_service.html",
        "breadcrumb":"Service"
        },
    "storage":{
        "name":"Storage configuration",
        "short":"Storage",
        "desc":"Content storage for your users",
        "type":"single",
        "icon":"fa fa-hdd-o",
        "section": "storage",
        "template":"cfg_storage.html",
        "breadcrumb":"Location"
        }
    }


@app.route("/config")
def config_index():
    """
    this route only lists the available sections.
    """
    return render_template("config/index.html",
                           sections=configuration_groups
                           )

def get_config_reader():
    conf_parser = ConfigParser();
    conf_parser.read("config.ini")

    return conf_parser


def get_group_sections(config_reader, group):
    """
    Gets the sections that are relevant to a specific group.
    """

    # If the group we're being asked for doesn't exist, return None
    # This is mostly a sanity check.
    if group not in configuration_groups.keys():
        return None
    # Get the list of sections that are within this group's namespace
    this_group = configuration_groups[group]
    
    # Sanity check: Is the group we're working a multi?
    # Plurals can only be used by multi-section groups.
    if this_group["type"] != "multi":
        return None

    # now, we're going to find the sections that match the group's prefix.
    filter_func = lambda section: section.startswith(this_group["namespace"]+".")

    this_group_sections = list(filter(filter_func, config_reader.sections()))

    # We need a small amount of post-processing here, however.
    this_group_subpages = []
    for section in this_group_sections:
        # do a thing
        this_subpage = {
            "name":section,
            "group":group
            }
        prefixlen=len(this_group["namespace"])+1
        # we need to fill in `label` as appropriate.
        shortname = section[prefixlen::]
        if config_reader.has_option(section, "type"):
            this_subpage["template"] = "cfg_{0}_{1}.html".format( this_group["namespace"], config_reader.get(section, "type"))
        else:
            this_subpage["template"] = this_group["template"]
        if config_reader.has_option(section, "ui_label"):
            this_subpage["label"] = "{0} ({1})".format(config_reader.get(section, "ui_label"), shortname)
        else:
            this_subpage["label"] = shortname
        this_group_subpages.append(this_subpage)
    return this_group_subpages


###

## We're going to re-work how we handle configuration pages.
# What we want is to make the format
# /config/<section>

@app.route('/config/<section>')
def config_section(section):
    """
    This configures a specific section of the configuration file
    """

    # get a handle on the configuration reader
    config_reader = get_config_reader()

    # First we want to know if it's a top-level group.
    # If so, we're going to render its page.

    # Get the current options for the section. 
    config_options = config_reader.items(section)
     
    # Find the group that this section belongs to.
    # When we're in a namespaced section, we'll be in the group that the namespace belongs to.
    current_group = None
    is_child = False
    for group in configuration_groups:
        if section == group["section"]:
            current_group = group
            break
        else:
            # Check to see if our section is a child of the group
            if configuration_groups[group]["type"] == multi:
                # We want to know if the namespace of that group matches.
                namespace = configuration_groups[group]["namespace"]
                if section.startswith(namespace+"."):
                    current_group = group
                    is_child = True
                    break

    # If this search returned nobody, this section cannot be configured through the web interface.
    if current_group == None:
        abort(500)


    cgroupdict = configuration_groups[current_group]

    # We now need to know what template to use for this.
    # we do this by building a list of possible templates. 
    
    templates = [ cgroupdict["template"],  'cfg_generic.html']

    if cgroupdict['type'] == 'multi':
        templates.insert(0, "cfg_"+cgroupdict['namespace'])

    # we need to pass in the current section, the sections 

    pass




###

@app.route("/config/x/<group>")
def config_group(group):
    """
    this route gets a specific section. If that section is a single section, it shows it.
    otherwise, it lists the known configuration points within that section. 
    """

    # TODO: return a 404. 
    if group not in configuration_groups.keys():
        abort(404)

    group_dict = configuration_groups[group]

    conf_parser = get_config_reader();


    if group_dict["type"] == "multi":

        current_subpages = get_group_sections(conf_parser, group)

        # return the rendered page.
        return render_template(
            'config/base.html',
            current_page=group,
            config_pages=configuration_groups,
            current_subpage=None,
            subpages = current_subpages
            )
    else:
        config_values = dict(conf_parser.items(group_dict["section"]))

        try:
            # Attempt to render the configuration group's page.
            return render_template(
                "config/"+config_group["template"],
                current_page=group,
                config_pages=configuration_groups,
                values=config_values,
                ini_section=group
                )
        except:
            return render_template(
                "config/cfg_generic.html",
                current_page=group,
                config_pages=configuration_groups,
                values=config_values,
                ini_section=group
                )

    return render_template(
        'config/base.html',
        current_page=group,
        config_pages=configuration_groups
        )

@app.route("/config/<group>/<item>")
def config_item(group, item):
    config_reader = get_config_reader();

    # get the current page.

    subpages = get_group_sections(config_reader, group)

    # todo: this is magic. document it.

    tSubpage = list(filter(lambda x: x["name"] == item and x["group"] == group, subpages )) 
    if(len(tSubpage)>1):
        abort(500)
    else:
        tSubpage = tSubpage[0]

    # We need the current state of the configuration of that section

    config_options = dict(filter( lambda i: i[0] != 'ui_label' and i[0] != 'type', list(config_reader.items(item))))

    possible_templates = (tSubpage["template"], configuration_groups[group]["template"], "cfg_generic.html")

    for template in possible_templates:
        try:
            return render_template(
                "config/"+template,
                current_page=group,
                current_subpage = item,
                config_pages = configuration_groups,
                subpages = subpages,
                values = config_options,
                ini_section=item
                )
        except:
            continue
    # this should not be a 5xx -- should it?
    abort(500)


@app.route('/config/write/<section>', methods=['POST'])
def write_config(section):
    """
    this method takes a section and writes it to the configuratiom file as requested.

    we can get away with this because we read the configuration every time we load a page. 
    this means we always have a fresh copy of the configuration. 

    TODO: we need to implement this. This needs the app search paths work done so this works.
    that will give us the file we want to write to, as the primary config is likely in a read only place.

    TODO: does this need to know the section before hand or can we pass that in via the POST data?
    I don't think it's a bad idea to have it as part of the url part. This would make the request a little nicer looking. It also has the advantage of making it possible to
    look a little futher ahead and see if we need to do anything special to the file we're editing: this lets us choose to ban certain sections from being edited easier. 


    """
    abort(500)
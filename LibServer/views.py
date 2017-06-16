"""
This is the administration view for Alexandria's LibServ

this handles making sure that the user is logged in and allows the user to change settings, as well as 
several other administration tasks such as restarting the device or restarting services.
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
        "section":"services",
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

# this is mostly for the UI.
# This generates a set of small dictionaries that are used to generate the
# sidebar of the admin page.
def get_sidebar():
    config_reader = get_config_reader() 
    # We're going to read through each section type and try to generate a sidebar.
    sidebar = configuration_groups.copy()
    # We need to copy the configuration groups because otherwise we modify the original.
    # Python does this. 
    for group in sidebar:
        cGroup = sidebar[group]
        # check to see if this is a multi group
        # if it is, then we need to fetch the groups 
        if cGroup["type"] == "multi":
            # add a chilren item to this item.
            # This is how we can render the children of this. 
            # This also has a nice little effect of possibly just listing 
            # all the available sections in the sidebar.
            cGroup["children"] = []
            child_sections = filter( lambda i: i.startswith(cGroup["namespace"] + "." ),  config_reader.sections())

            for section in child_sections:
                # We're going to add each item here to a submenu.
                # The template will be sorted out later.
                child_options = dict(config_reader.items(section))
                cchild_dict = {
                    "name":child_options["ui_label"],
                    "section":section
                    }
                cGroup["children"].append(cchild_dict)
        sidebar[group] = cGroup
    
    # We now have a worthwhile sidebar.
    return sidebar

@app.route("/config")
def config_index():
    """
    this route only lists the available sections.
    """
    return render_template("config/index.html",
                           groups=configuration_groups
                           )

def get_config_reader():
    conf_parser = ConfigParser();
    conf_parser.read(app.config["configfiles"])

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
    # Find the group that this section belongs to.
    # When we're in a namespaced section, we'll be in the group that the namespace belongs to.
    current_group = None
    is_child = False
    for group in configuration_groups:
        if section == configuration_groups[group]["section"]:
            current_group = group
            break
        else:
            # Check to see if our section is a child of the group
            if configuration_groups[group]["type"] == 'multi':
                # We want to know if the namespace of that group matches.
                namespace = configuration_groups[group]["namespace"]
                if section.startswith(namespace+"."):
                    current_group = group
                    is_child = True
                    break

    # If this search returned nobody, this section cannot be configured through the web interface.
    if current_group == None:
        abort(404)


    config_options_raw = {}
    if config_reader.has_section(section):
        config_options_raw = dict(config_reader.items(section))
     

    cgroupdict = configuration_groups[current_group]

    sidebar = get_sidebar()

    # we're going to filter the raw items handed to the template from the
    # configuration files. This makes it harder for the generic template to
    # mess something up unintentionally.

    config_options_cooked = {}
    for config_key in config_options_raw.keys():
        if config_key == "type" or config_key == "ui_label":
            continue
        else:
            config_options_cooked[config_key] = config_options_raw[config_key]
    # now, config_items_cooked has our filtered keys.
    # TODO: Make the above easier to extend

    
    # walk through templates and render them in order of likelyhood
    # there are a set of templates that need to be considered here:
    # in order of specificity,
    #
    # if we are looking at a wireless interface (interface.wlan0),
    # we want to have each of the following templates considered:
    #
    # * cfg_interface_wlan0.html
    # * cfg_interface_wireless.html
    # * cfg_interface.html
    # * cfg_generic.html
    #
    # for some types, we need the sequence to be a little different
    # such as in the case of services.
    # 
    # * cfg_service_ssh.html
    # * cfg_service.html
    # * cfg_generic.html
    #
    # We do this by replacing any .'s with _ first, then using that.
    # The namespace of the selected group is then checked:
    # 
    # cfg_{namespace}_{type}
    # cfg_{namespace}
    # cfg_generic
    #
    #
    # This means that the best way of handling this is to use the
    # following hierarchy:
    #
    # cfg_{section}.html            -- the most specific
    # cfg_{namespace}_{type}.html   -- Not as specific but works for interface.
    # cfg_{namespace}.html          -- A nice fallback for services.
    # cfg_generic.html              -- Fallback for all others.
    # 
    # this means that service.ssh will default use the template
    # cfg_service_ssh
    # Then will use `cfg_service.html` (which should exist.) then
    # as a worst case scenario will fall back on `cfg_generic.html`
    #   
    templates = []
    templates.append('cfg_{0}.html'.format(section.replace('.','_')))
    if 'type' in config_options_raw:
        # This only works on some sections as a section is responsible for
        # declaring its type.
        # This means we need to check. This also is only really relevant to the
        # multi section type of group, but this does make things simple.
        templates.append(
            'cfg_{0}_{1}.html'.format(
                cgroupdict['namespace'],
                config_options_raw['type']
                )
            )
    if 'namespace' in cgroupdict:
        templates.append('cfg_{0}.html'.format(cgroupdict['namespace']))
    templates.append('cfg_generic.html')
    for template in templates:
        # at this point, we are going to try rendering each template in order
        # and move on if there is a problem.
        # It's not an elegant solution but it works.

        # passed to template:
        # current sectiom
        # list of options in section
        # list of section groups
        # possibly list of child sections

        try:
            return render_template(
                "config/"+template,
                sidebar=sidebar,
                current_group=current_group,
                current_section=section,
                values=config_options_cooked
                )
        except Exception as e:
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

    """
    return(redirect(url_for('config_section', section=section)))
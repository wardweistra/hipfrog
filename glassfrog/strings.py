succes_color = 'green'

error_color = 'red'

install_message = 'Install HipFrog in your Hipchat room'

help_hipfrog = '''Use one of the following commands to learn more:
<ul>
<li><code>/circle [circle-name [members/roles]]</code>
 - List the circles in your organization</li>
<li><code>/role role-name</code>
 - Get the details for a role</li>
<li><code>@role [circle-name:]role-name</code>
 - Mention the people in the current room fullfilling the specified role</li>
<li><code>@circle circle-name</code>
 - Mention the people in the current room in the specified circle</li>
</ul>'''

help_hipfrog_circle = '''<strong>More</strong>:
<ul>
<li><code>/circle circle-name [members/roles]</code>
 - Get the details for the specified circle</li>
<li><code>@circle circle-name</code>
 - Mention the people in the current room in the specified circle</li>
</ul>'''

help_hipfrog_circle_circleid = '''<strong>More:</strong>
<ul>
<li><code>/circle {0} members</code>
 - List the members of the specified circle</li>
<li><code>/circle {0} roles</code>
 - List the roles and subcircles in the specified circle</li>
<li><code>@circle {0}</code>
  - Mention the people in the current room in the specified circle</li>
</ul>'''

help_hipfrog_circle_circleid_roles = '''
<li><code>/role role-name</code>
 - Get the details for a role</li>
<li><code>@role [circle-name:]role-name</code>
  - Mention the people in the current room fullfilling the specified role</li>'''

help_hipfrog_circle_circleid_subcircles = '''
<li><code>/circle [circle-name [members/roles]]</code>
 - List the circles in your organization</li>
<li><code>@circle circle-name</code>
 - Mention the people in the current room in the specified circle</li>'''

help_hipfrog_role_roleid = '''<strong>More:</strong>
<ul>
<li><code>@role {0}:{1}</code>
  - Mention the people in the current room fullfilling the specified role</li>
</ul>'''

set_token_first = "Please set the Glassfrog Token first in the plugin configuration"

installed_successfully = ('Installed successfully.'
                          ' Please set Glassfrog Token in the Hipchat Integration Configure page.')

configured_successfully_flash = 'Valid Glassfrog Token stored'

configured_successfully = "Configured successfully. Type <code>/hipfrog</code> to get started!"

missing_functionality = ("Sorry, the feature \'{}\' does not exist (yet)."
                         " Type <code>/hipfrog</code> to get a list of the available commands.")

circles_missing_functionality = ("Sorry, the feature \'{}\' does not exist (yet)."
                                 " Type <code>/circle {}</code> to get a list of"
                                 " the available commands.")

# Regex patterns for registering with Hipchat
regex_hipfrog = "\\A\\/[hH][iI][pP][fF][rR][oO][gG]\\b"
regex_slash_role = "\\A\\/[rR][oO][lL][eE][sS]?\\b"
regex_slash_circle = "\\A\\/[cC][iI][rR][cC][lL][eE][sS]?\\b"
regex_at_role = "@[rR][oO][lL][eE][sS]?\\b"
regex_at_circle = "@[cC][iI][rR][cC][lL][eE][sS]?\\b"

# Regex patterns for Python code
regex_at_role_roleId = "@[rR][oO][lL][eE][sS]? ([\w\-\:]+)"
regex_at_circle_circleId = "@[cC][iI][rR][cC][lL][eE][sS]? ([\w\-]+)"

no_circle_matched = 'No circle name matched {}'
no_role_matched = 'No role name matched {}'
no_role_in_circle_matched = 'No role name in circle {0} matched {1}'

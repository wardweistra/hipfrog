succes_color = 'green'

error_color = 'red'

install_message = 'Install HipFrog in your Hipchat room'

help_hipfrog = '''Use one of the following commands to learn more:
<ul>
<li><code>/hipfrog circles ([Circle ID] (members/roles))</code>
 - List the circles in your organization</li>
<li><code>/hipfrog role [Role ID]</code>
 - Get the details for a role</li>
<li><code>@role [Role ID]</code>
 - Mention the people in the current room fullfilling the specified role</li>
<li><code>@circle [Circle ID]</code>
 - Mention the people in the current room in the specified circle</li>
</ul>'''

help_hipfrog_circle = '''<strong>More</strong>:
<ul>
<li><code>/hipfrog circle [Circle ID] (members/roles)</code>
 - Get the details for the specified circle</li>
<li><code>@circle [Circle ID]</code>
 - Mention the people in the current room in the specified circle</li>
</ul>'''

help_hipfrog_circle_circleid = '''<strong>More:</strong>
<ul>
<li><code>/hipfrog circle {0} members</code>
 - List the members of the specified circle</li>
<li><code>/hipfrog circle {0} roles</code>
 - List the roles and subcircles in the specified circle</li>
<li><code>@circle {0}</code>
  - Mention the people in the current room in the specified circle</li>
</ul>'''

help_hipfrog_circle_circleid_roles = '''<strong>More:</strong>
<ul>
<li><code>@role [Role ID]</code>
  - Mention the people in the current room fullfilling the specified role</li>
<li><code>@circle [Circle ID]</code>
 - Mention the people in the current room in the specified circle</li>
</ul>'''


set_token_first = "Please set the Glassfrog Token first in the plugin configuration"

installed_successfully = ('Installed successfully.'
                          ' Please set Glassfrog Token in the Hipchat Integration Configure page.')

configured_successfully_flash = 'Valid Glassfrog Token stored'

configured_successfully = "Configured successfully. Type <code>/hipfrog</code> to get started!"

missing_functionality = ("Sorry, the feature \'{}\' does not exist (yet)."
                         " Type <code>/hipfrog</code> to get a list of the available commands.")

circles_missing_functionality = ("Sorry, the feature \'{}\' does not exist (yet)."
                                 " Type <code>/hipfrog circle {}</code> to get a list of"
                                 " the available commands.")

regex_hipfrog = "\\A\\/[hH][iI][pP][fF][rR][oO][gG]\\b"
regex_at_role = "@[rR][oO][lL][eE]"
regex_at_role_roleId = "@[rR][oO][lL][eE] (\w+)"
regex_at_circle = "@[cC][iI][rR][cC][lL][eE]"
regex_at_circle_circleId = "@[cC][iI][rR][cC][lL][eE] (\w+)"

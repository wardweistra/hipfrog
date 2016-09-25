succes_color = 'green'

error_color = 'red'

install_message = 'Install HipFrog in your Hipchat room'

help_hipfrog = '''Use one of the following commands to learn more:
<ul><li><code>/hipfrog circles</code> - List the circles in your organization</li></ul>'''

help_hipfrog_circle = '''More:
<ul>
<li><code>/hipfrog circle [Circle ID]</code> - Get the details for this circle</li>
</ul>'''

help_hipfrog_circle_circleid = '''<strong>More:</strong>
<ul>
<li><code>/hipfrog circle {0} members</code> - List the members of this circle</li>
<li><code>/hipfrog circle {0} roles</code> - List the roles in this circle</li>
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

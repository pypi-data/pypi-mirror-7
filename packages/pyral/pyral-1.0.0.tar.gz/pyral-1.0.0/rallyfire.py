#!/usr/bin/env python

#################################################################################################
#
#  rallyfire - Examplar script to test the basic connectivity to a Rally server
#              and obtain basic workspace and project information
#
#################################################################################################

import sys

from pyral import Rally, rallySettings

#################################################################################################

errout = sys.stderr.write

#################################################################################################

def main(args):
    options = [opt for opt in args if opt.startswith('--')]
    args    = [arg for arg in args if arg not in options]
    server, user, password, workspace, project = rallySettings(options)
    print " ".join(["|%s|" % item for item in [server, user, password, workspace, project]])
    rally = Rally(server, user, password, workspace=workspace, project=project) 
    #rally = Rally(server, user, password, debug=True)
    rally.enableLogging('fire.log')
    # add in the debug=True keyword arg if you want more verbiage ...
    #rally = Rally(server, user, password, workspace=workspace, project=project, debug=True) 
    specified_workspace = workspace

    workspace = rally.getWorkspace()
    print "Workspace: %s " % workspace.Name
    if specified_workspace != workspace.Name:
        print "    ** The workspace you specified: %s is not a valid workspace name for your account, using your default  workspace instead" % specified_workspace
    #print "Workspace: %12.12s   %-18.18s    (%s)" % (workspace.oid, workspace.Name, workspace.ref)

    project = rally.getProject()
    print "Project  : %s " % project.Name
    #print "Project  : %12.12s   %-18.18s    (%s)" % (project.oid, project.Name, project.ref)

    # uncomment this to see all of your accessible workspaces and projects
#    workspaces = rally.getWorkspaces()
#    for workspace in workspaces:
#        print " ", workspace.Name
#        projects = rally.getProjects(workspace=workspace.Name)
#        if projects:
#            print ""
#            print "    Projects:"
#            for project in projects:
#                print "     ", project.Name
#        else:
#            print "  No projects"
#        print ""

    sys.exit(0)

#################################################################################################
#################################################################################################

if __name__ == '__main__':
    main(sys.argv[1:])

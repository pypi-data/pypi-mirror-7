*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Test cases ***

Create Blog, subobjects and test views
    Enable Autologin as  Site Administrator
    Go to Homepage

    # create a blog without image
    Open Add New Menu
    Click Link  css=a#blog
    Page Should Contain  Add Blog
    Input Text  css=#form-widgets-IDublinCore-title  It's a Blog
    Input Text  css=#form-widgets-author  HJS

    Click Button  Save
    Page Should Contain  Item created

    # verify the blog header is visible
    Element Should Be Visible  css=#blog-header
    # check the title is visible
    Element Should Be Visible  css=.documentFirstHeading

    # edit the blog and add an image
    Click Link  link=Edit
    Choose File  css=#form-widgets-image-input  /tmp/img1.jpg
    Click Button  Save
    Page Should Contain  Changes saved

    # check the title is now an attribute of the image
    Element Should Be Visible  xpath=//img[@title="It's a Blog"]
    Element Should Be Visible  xpath=//img[@alt="It's a Blog"]

    # add a post
    Open Add New Menu
    Click Link  css=a#document
    Page Should Contain  Add Page
    Input Text  css=#title  First Post
    Click Button  Save
    Page Should Contain  Changes saved

    # verify the post is listed in the blog
    Click Link  link=It's a Blog
    Page Should Contain  First Post

    # open the post
    Click Link  link=First Post
    # verify the blog header is visible
    Element Should Be Visible  css=#blog-header

    # create a folder
    Click Link  link=It's a Blog
    Open Add New Menu
    Click Link  css=a#folder
    Page Should Contain  Add Folder
    Input Text  css=#title  SubFolder
    Click Button  Save
    Page Should Contain  Changes saved

    # create a post inside the folder
    Open Add New Menu
    Click Link  css=a#document
    Page Should Contain  Add Page
    Input Text  css=#title  Second Post
    Click Button  Save
    Page Should Contain  Changes saved

    # verify the second post is listed in the blog
    Click Link  link=It's a Blog
    Page Should Contain  First Post
    Page Should Contain  Second Post

    # open the second post
    Click Link  link=Second Post
    # verify the blog header is visible
    Element Should Be Visible  css=#blog-header

    # change the blog view
    Click Link  link=It's a Blog
    Open Display Menu
    Click Link  css=a#plone-contentmenu-display-blog_summary_view

    # verify the new view
    Page Should Contain  First Post
    Page Should Contain  Second Post

    # delete the blog
    Open Action Menu
    Click Link  css=a#plone-contentmenu-actions-delete
    Click Button  Delete
    Page Should Contain  Plone site
    Go to Homepage
    Page Should Not Contain Element  css=#portaltab-its-a-blog


Create Blog test views using VHM
    Enable Autologin as  Site Administrator
    Go to Homepage

    # create a blog without image
    Open Add New Menu
    Click Link  css=a#blog
    Page Should Contain  Add Blog
    Input Text  css=#form-widgets-IDublinCore-title  BlogVHM
    Input Text  css=#form-widgets-author  HJS
    Click Button  Save
    Page Should Contain  Item created

    # add a post
    Open Add New Menu
    Click Link  css=a#document
    Page Should Contain  Add Page
    Input Text  css=#title  PostVHM
    Click Button  Save
    Page Should Contain  Changes saved

    # verify the post is listed in the blog
    Click Link  link=BlogVHM
    Page Should Contain  PostVHM

    # open the post
    Click Link  link=PostVHM
    # verify the blog header is visible
    Element Should Be Visible  css=#blog-header

    # open with VHM url
    Open Browser  http://localhost:${ZOPE_PORT}/VirtualHostBase/http/127.0.0.1:${ZOPE_PORT}/VirtualHostRoot/plone/blogvhm
    Page Should Contain  PostVHM
    Click Link  link=PostVHM
    Element Should Be Visible  css=#blog-header

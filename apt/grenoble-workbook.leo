<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<?xml-stylesheet ekr_test?>
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="maphew.20140920000632.1627"><vh>Startup</vh>
<v t="maphew.20140920000632.1628"><vh>@button make-sphinx</vh></v>
<v t="maphew.20140920000632.1629"><vh>@settings</vh>
<v t="maphew.20140920000632.1630"><vh>@string target_language = rest</vh></v>
<v t="maphew.20140920000632.1631"><vh>For rst3 command</vh>
<v t="maphew.20140920000632.1632"><vh>@bool rst3_call_docutils = True</vh></v>
<v t="maphew.20140920000632.1633"><vh>@bool rst3_write_intermediate_file = True</vh></v>
<v t="maphew.20140920000632.1634"><vh>@string rst3_write_intermediate_extension = .txt</vh></v>
</v>
</v>
</v>
<v t="maphew.20140920000632.1653"><vh>Leo's cheat sheet</vh>
<v t="maphew.20140920000632.1654"><vh>Key bindings</vh>
<v t="maphew.20140920000632.1655"><vh>Selecting outline nodes</vh></v>
<v t="maphew.20140920000632.1656"><vh>Moving outline nodes</vh></v>
<v t="maphew.20140920000632.1657"><vh>Moving the cursor</vh></v>
</v>
<v t="maphew.20140920000632.1658"><vh>Frequently used commands</vh></v>
<v t="maphew.20140920000632.1659"><vh>Leo directives</vh></v>
<v t="maphew.20140920000632.1660"><vh>Settings</vh></v>
<v t="maphew.20140920000632.1661"><vh>Node types</vh></v>
<v t="maphew.20140920000632.1662"><vh>Notable Plugins</vh></v>
<v t="maphew.20140920000632.1663"><vh>External files (@&lt;file&gt; nodes)</vh></v>
<v t="maphew.20140920000632.1664"><vh>Scripting</vh>
<v t="maphew.20140920000632.1665"><vh>Pre-defined symbols</vh></v>
<v t="maphew.20140920000632.1666"><vh>Generators</vh></v>
<v t="maphew.20140920000632.1667"><vh>Commands class</vh></v>
<v t="maphew.20140920000632.1668"><vh>vnode class</vh></v>
<v t="maphew.20140920000632.1669"><vh>position class</vh></v>
<v t="maphew.20140920000632.1670"><vh>leo.core.leoGlobals module</vh></v>
</v>
</v>
<v t="maphew.20140920000632.1681"><vh>The rst3 tutorial</vh>
<v t="maphew.20140920000632.1682"><vh>@rst ~/myDocument.html</vh>
<v t="maphew.20140920000632.1683"><vh>Chapter I</vh>
<v t="maphew.20140920000632.1684"><vh>@rst-ignore</vh></v>
</v>
<v t="maphew.20140920000632.1685"><vh>@rst-ignore-tree Chapter 2+</vh>
<v t="maphew.20140920000632.1686"><vh>Chapter II</vh>
<v t="maphew.20140920000632.1687"><vh>translation</vh></v>
</v>
</v>
<v t="maphew.20140920000632.1688"><vh>Chapter XII</vh></v>
<v t="maphew.20140920000632.1689"><vh>@rst-no-head The End</vh></v>
</v>
<v t="maphew.20140920000632.1690"><vh>~/myDocument.html.txt</vh></v>
</v>
<v t="maphew.20140920000632.1691" a="E"><vh>apt</vh>
<v t="maphew.20140922213912.1720" a="E"><vh>by flow</vh>
<v t="maphew.20140922213912.1721"><vh>Setup</vh>
<v t="maphew.20140927121126.1789"><vh>INSTALLED.DB</vh></v>
<v t="maphew.20100223163802.3732"><vh>setup</vh></v>
<v t="maphew.20100223163802.3764"><vh>write_installed</vh></v>
<v t="maphew.20100223163802.3733"><vh>update</vh></v>
</v>
</v>
<v t="maphew.20140927120559.1738" a="E"><vh>@path b:/code/gcode/apt</vh>
<v t="maphew.20140927120937.1659"><vh>@file apt.py</vh></v>
<v t="maphew.20140927121126.1736" a="E"><vh>@auto dapt.py</vh></v>
<v t="maphew.20140927121126.1730"><vh>@auto setup.py</vh></v>
</v>
<v t="maphew.20140920004020.1708"><vh>@path b:/code/apt-click</vh>
<v t="maphew.20140924233019.1730"><vh>@auto chunk.py</vh></v>
<v t="maphew.20140920004020.1709"><vh>@auto clapt.py</vh></v>
</v>
</v>
<v t="maphew.20140927121126.1732"><vh>@persistence</vh>
<v t="maphew.20140927121126.1733"><vh>@data:@auto setup.py</vh>
<v t="maphew.20140927121126.1735"><vh>@gnxs</vh></v>
</v>
<v t="maphew.20140927121126.1737"><vh>@data:@auto dapt.py</vh>
<v t="maphew.20140927121126.1825"><vh>@gnxs</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="maphew.20100223163802.3732">def setup ():
    '''skeleton installed packages environment'''
    if not os.path.isdir (root):
        sys.stderr.write ('Root dir not found, creating %s\n' % root)
        os.makedirs (root)
    if not os.path.isdir (config):
        sys.stderr.write ('creating %s\n' % config)
        os.makedirs (config)
    if not os.path.isfile (installed_db):
        sys.stderr.write ('creating %s\n' % installed_db)
        global installed
        installed = {0:{}}
        write_installed ()
    if not os.path.isfile (setup_ini):
        sys.stderr.write ('getting %s\n' % setup_ini)
        update ()

</t>
<t tx="maphew.20100223163802.3733">def update ():
    '''setup.ini'''
    if not os.path.exists (downloads):
        os.makedirs (downloads)

    source = mirror + '/setup.ini.bz2'
    archive = downloads + 'setup.ini.bz2'

    # backup existing setup config
    if os.path.exists (setup_ini):
        if os.path.exists (setup_bak):
                os.remove (setup_bak)
        os.rename (setup_ini, setup_bak)

   # remove cached ini
    if os.path.exists (archive):
        os.remove (archive)

   # get current ini
    f = urllib.urlretrieve(source, archive, down_stat)
    uncompressedData = bz2.BZ2File(archive).read()

    # save uncompressed ini to setup dir
    ini = open(setup_ini, 'w')
    ini.write(uncompressedData)
    ini.close

</t>
<t tx="maphew.20100223163802.3764">def write_installed ():
    # ''' Record package in install.db '''
    file = open (installed_db, 'w')
    file.write (installed_db_magic)
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise 'urg'

</t>
<t tx="maphew.20140920000632.1627">By convention, a Startup node contains settings, scripts, etc.
that mostly one wants to have hidden.
</t>
<t tx="maphew.20140920000632.1628">@language python
import os
trace = True
g.cls()
c.setComplexCommand('make-sphinx')
c.save()
aList = c.rstCommands.rst3()
if aList:
    path = g.os_path_finalize_join(g.app.loadDir,'..','doc','html')
    os.chdir(path)
    if len(aList) &gt; 1: g.execute_shell_commands('make clean',trace=trace)
    g.execute_shell_commands('make html',trace=trace)
    fn = aList[0].h.strip() if len(aList) == 1 else 'leo_toc.html'
    fn = g.os_path_finalize_join(path,'_build','html',g.os_path_basename(fn))
    if g.os_path_exists(fn):
        # Don't wait for this command to exit!
        g.execute_shell_commands(['&amp;%s' % (fn)],trace=trace)
</t>
<t tx="maphew.20140920000632.1629">**Imortant**: to take effect, all settings must be descendants of this
@settings node.

**Note**: This file colors text as reStructuredText by default because of
the setting::

    @string target_language = rest
</t>
<t tx="maphew.20140920000632.1630">The default language if no @language or @comment is in effect.

Valid values are (case is ignored):

actionscript,c,csharp,css,cweb,elisp,html,java,latex,
pascal,perl,perlpod,php,plain,plsql,python,rapidq,rebol,shell,tcltk.</t>
<t tx="maphew.20140920000632.1631"></t>
<t tx="maphew.20140920000632.1632"># Use False when using Sphinx</t>
<t tx="maphew.20140920000632.1633"></t>
<t tx="maphew.20140920000632.1634"></t>
<t tx="maphew.20140920000632.1653"></t>
<t tx="maphew.20140920000632.1654"></t>
<t tx="maphew.20140920000632.1655">When focus is in the outline pane::

    Right-arrow (expand-and-go-right)
    Left-arrow (contract-or-go-left)
    Up-arrow (goto-prev-visible) 
    Down-arrow (goto-next-visible)
    
Regardless of focus::

    Alt-Home (goto-first-visible-node) 
    Alt-End (goto-last-visible-node)
    Alt-Right-arrow (expand-and-go-right)
    Alt-Left-arrow (contract-or-go-left)
    Alt-Up-arrow (goto-prev-visible) 
    Alt-Down-arrow (goto-next-visible)
</t>
<t tx="maphew.20140920000632.1656">When focus is in the outline::

    Shift-Down-arrow (move-outline-down) 
    Shift-Left-arrow (move-outline-left) 
    Shift-Right-arrow (move-outline-right) 
    Shift-Up-arrow (move-outline-up)

Regardless of focus::

    Alt-Shift-Down-arrow (move-outline-down) 
    Alt-Shift-Left-arrow (move-outline-left) 
    Alt-Shift-Right-arrow (move-outline-right) 
    Alt-Shift-Up-arrow (move-outline-up)
    Ctrl-D (move-outline-down)
    Ctrl-L (move-outline-left) 
    Ctrl-R (move-outline-right)
    Ctrl-U (move-outline-up)
</t>
<t tx="maphew.20140920000632.1657">When focus is in any of Leo's text panes (body pane, log pane, headlines):

    +-------------------+-----------------------+
    | **Key**           | **Move Cursor**       |
    +-------------------+-----------------------+
    | Arrow keys        | one character         |
    +-------------------+-----------------------+
    | Ctrl-LeftArrow    | back one word         |
    +-------------------+-----------------------+
    | Ctrl-RightArrow   | forward one word      |
    +-------------------+-----------------------+
    | Home              | beginning of line     |
    +-------------------+-----------------------+
    | End               | end of line           |
    +-------------------+-----------------------+
    | Ctrl-Home         | beginning of the body |
    +-------------------+-----------------------+
    | Ctrl-End          | end of body           |
    +-------------------+-----------------------+
    | PageDown          | down one page         |
    +-------------------+-----------------------+
    | PageUp            | up one page           |
    +-------------------+-----------------------+
    
Adding the Shift key modifier to any of the keys above
moves the cursor and extends the selected text.
</t>
<t tx="maphew.20140920000632.1658">For much more information, see Leo's Commands Reference: http://leoeditor.com/commands.html

Copy/Paste (text)::

    Ctrl-C (copy-text)
    Ctrl-K (kill)
    Ctrl-V (paste-text)
    Ctrl-X (cut-text)
    Ctrl-Y (yank)
    Alt-Y  (yank-pop)
    kill-...

Files::

    Ctrl-N (new) 
    Ctrl-O (open-outline)
    Ctrl-S (save-file) 
    Ctrl-Q (exit-leo)

Focus::

    Alt-T (focus-to-tree) 
    Ctrl-T (toggle-active-pane)
    Ctrl-Tab (tab-cycle-next)
    
Help::

    Alt-0 (vr-toggle)
    F1 (help) 
    F11 (help-for-command) 
    F12 (help-for-python)
    print-bindings
    print-settings
    help-for-...

Find/Replace::

    Ctrl-F (search-with-present-options) 
    Shift-Ctrl-R (replace-string)
    Ctrl-minus (replace-then-find) 
    F3 (find-next) 
    F2 (find-previous)
    
Minibuffer::

    Alt-X (full-command)
    Ctrl-G (keyboard-quit)

Nodes::

    Ctrl-I or Insert (insert-node)
    Ctrl-H (edit-headline)
    &lt;Return&gt; (when editing a headline) (end-edit-headline)
    Ctrl-Shift-C (copy-node)
    Ctrl-Shift-X (cut-node) 
    Ctrl-Shift-V (paste-node) 
    Ctrl-{ (promote)
    Ctrl-} (demote)
    Ctrl-M (mark) 

Undo::

    Ctrl-Z (undo)
    Ctrl-Shift-Z (redo)
</t>
<t tx="maphew.20140920000632.1659">Directives starting with '@ in the leftmost column
    
For full details, see Leo's Directives reference: http://leoeditor.com/directives.html

    @                       # starts doc part
    @c                      # ends doc part
    @color
    @doc                    # starts doc part
    @killcolor
    @nocolor
    @language python
    @language c
    @language rest          # restructured text
    @language plain         # plain text: no syntax coloring.
    @lineending lineending
    @pagewidth 100
    @raw, @end_raw          # @file only.
    @tabwidth -4            # use spaces
    @tabwidth 8             # use tabs
    @nowrap
    @wrap
    
Leading whitespace is allowed (and significant) for::

    @all
    @others
    </t>
<t tx="maphew.20140920000632.1660">For documentation see node: "About this file" in leoSettings.leo.

- Key bindings:     @shortcuts
- Visual settings:  @data qt-gui-plugin-style-sheet
- Enabling plugins: @enabled-plugins

To disable a binding for a key, bind it to do-nothing::

    do-nothing = Insert
    
This overrides the following default binding in leoSettings.leo::

    insert-node = Insert
</t>
<t tx="maphew.20140920000632.1661">Supported by Leo's core:

- @chapters, @chapter
- @rst, @rst-no-head, @rst-ignore, @rst-ignore-tree
- @settings
- @test, @testsetup, @testclass
- @url

Within @settings trees:

- @bool, @color, @directory, @encoding, @int
- @float, @font, @ratio, @path, @string
- @enabled-plugins
- @buttons, @commands
- @menus, @menu, @menuat, @item
- @openwith, @shortcuts

Supported by plugins:

- bookmarks.py: @bookmarks, @bookmark
- at_folder.py: @folder
- at_produce.py: @produce
- at_view.py: @clip, @strip, @view
- expfolder.py: @expfolder
- mod_scripting.py: @button, @command, @script
- viewrendered.py: @graphics-script, @image, @html, @md, @movie and @svg
- rss.py: @feed

</t>
<t tx="maphew.20140920000632.1662">See the docstring of these plugins for more details:

- bookmarks.py: Manages URL's used as bookmarks.
- contextmenu.py: Brings up context menu when user right-clicks a headline.
- mod_scripting.py: Supports @button and @command nodes.
- quicksearch.py: Adds Nav tab for searching.
- todo.py: Manages to-do lists and simple project management.
- valuespace.py: Creates an outline-oriented spreadsheet.
- viewrendered.py: Creates a rendering pane. Automatically loaded by Leo's help commands.
</t>
<t tx="maphew.20140920000632.1663">\@&lt;file&gt; nodes create external files::

    @asis &lt;filename&gt;    
    @auto &lt;filename&gt;    
    @edit &lt;filename&gt;
    @file &lt;filename&gt;
    @nosent &lt;filename&gt;  
    @shadow &lt;filename&gt;
    
For full details, see Leo's Directives reference: http://leoeditor.com/directives.html
    
**Section names** have the form::

    &lt;&lt; any text, except double closing angle brackets &gt;&gt;
    
**Section-definition nodes** have headlines starting with a section name.

Leo performs **expansions** for all @&lt;file&gt; nodes except @asis.

Expansion of @all:

- Leo replaces @all by the *unexpanded* body text of *all* nodes.

Expansion of section names and @others:

- Leo replaces section names in body text by the *expanded*
  text of the corresponding section definition node.
  
- Leo replaces @others with the *expanded* text of all nodes
  that *aren't* section-definition nodes.
</t>
<t tx="maphew.20140920000632.1664">This section lists the ivars, properties, functions and methods most
commonly used in Leo scripts.

**Very important**: use Alt-1 (toggle-autocompleter) and Alt-2
(toggle-calltips) to recreate these lists as you type.

As an alternative to this chapter, Jacob Peck has written a more informal scripting tutorial:
http://blog.suspended-chord.info/2014/01/28/intro-to-leo-scripting/</t>
<t tx="maphew.20140920000632.1665">execute-script predefines::

    c: The commander of the present outline.
    g: The leo.core.leoGlobals module.
    p: The presently selected position, c.p.
    
@test scripts predefine all the above, plus::

    self: The instance of unittest.TestCase
</t>
<t tx="maphew.20140920000632.1666">::

    c.all_positions()
    c.all_unique_positions()
    p.children()
    p.parents()
    p.self_and_parents()
    p.self_and_siblings()
    p.following_siblings()
    p.subtree()
    p.self_and_subtree()
</t>
<t tx="maphew.20140920000632.1667">::

    c.frame         c's outer frame, a leoFrame instance.
    c.user_dict     a temporary dict for use of scripts and plugins.
    c.redraw()
    c.positionExists(p)

Here is a partial list of the **official ivars** of any leoFrame f::

    f.c                     is the frame’s commander.
    f.body                  is a leoBody instance.
    f.body.bodyCtl          is a leoQTextEditWidget instance.
    f.body.bodyCtrl.widget  is a LeoQTextBrowser(QTextBrowser) instance.
    f.log                   is a leoLog instance.
    f.tree                  is a leoQtTree instance.
    f.tree.treeWidget       is a LeoQTreeWidget (a QTreeWidget) instance.
    
Use autocompletion to explore these objects!
</t>
<t tx="maphew.20140920000632.1668">::

    v.b: v's body text.
    v.h: v's headline text.
    v.u: v.unknownAttributes, a persistent Python dictionary.
    
v.u (uA's or unknownAttributes or userAttributes) allow plugins or scripts
to associate persistant data with vnodes. For details see:
http://leoeditor.com/customizing.html#adding-extensible-attributes-to-nodes-and-leo-files
</t>
<t tx="maphew.20140920000632.1669">**Properties**::

    p.b: same as p.v.b.
    p.h: same as p.v.h.
    p.u: same as p.v.u.

**Getters**::

    p.back()
    p.children()
    p.firstChild()
    p.hasBack()
    p.hasChildren()
    p.hasNext()
    p.hasParent()
    p.hasThreadBack()
    p.hasThreadNext()
    p.isAncestorOf(p2)
    p.isAnyAtFileNode()
    p.isAt...Node()
    p.isCloned()
    p.isDirty()
    p.isExpanded()
    p.isMarked()
    p.isRoot()
    p.isVisible()
    p.lastChild()
    p.level()
    p.next()
    p.nodeAfterTree()
    p.nthChild()
    p.numberOfChildren()
    p.parent()
    p.parents()
    p.threadBack()
    p.threadNext()
    p.visBack()
    p.visNext()
    
**Setters**::

    p.setDirty()
    p.setMarked()

**Operations on nodes**::

    p.clone()
    p.contract()
    p.doDelete(new_position)
    p.expand()
    p.insertAfter()
    p.insertAsNthChild(n)
    p.insertBefore()
    p.moveAfter(p2)
    p.moveToNthChildOf(parent,n)
    p.moveToRoot(oldRoot=None)
        # oldRoot **must** be the old root position if it exists.
        
**Moving positions**

The following move positions *themselves*: they change the node to which a
position refers. They do *not* change outline structure in any way! Use
these when generators are not flexible enough::

    p.moveAfter(p2)
    p.moveToBack()
    p.moveToFirstChild()
    p.moveToFirstChildOf(p2)
    p.moveToLastChild()
    p.moveToLastChildOf(p2)
    p.moveToLastNode()
    p.moveToNext()
    p.moveToNodeAfterTree(p2)
    p.moveToNthChild()
    p.moveToNthChildOf(p2)
    p.moveToParent()
    p.moveToRoot()
    p.moveToThreadBack()
    p.moveToThreadNext()
    p.moveToVisBack(c)
    p.moveToVisNext(c)
</t>
<t tx="maphew.20140920000632.1670">For full details, see @file leoGlobals.py in LeoPyRef.leo.

**g vars**::

    g.app
    g.app.gui
    g.app.windowlist
    g.unitTesting
    g.user_dict  # a temporary dict for use of scripts and plugins.
    
**g decorator**::

    @g.command(command-name)
    
**g functions** (the most interesting: there are many more in leoGlobals.py)::
    
    g.angleBrackets()
    g.app.commanders()
    g.app.gui.guiName()
    g.es(*args,**keys)
    g.es_print(*args,**keys)
    g.es_exception()
    g.getScript(c,p,
        useSelectedText=True,
        forcePythonSentinels=True,
        useSentinels=True)
    g.openWithFileName(fileName,old_c=None,gui=None)
    g.os_path_... # Wrappers for os.path methods.
    g.pdb(message='')
    g.toEncodedString(s,encoding='utf-8',reportErrors=False)
    g.toUnicode(s, encoding='utf-8',reportErrors=False)
    g.trace(*args,**keys)
    g.warning(*args,**keys)
</t>
<t tx="maphew.20140920000632.1681">Here is an expanded version of the example from
http://leoeditor.com/tutorial-rst3.html

Control-click the URL above to open the page in your browser.

Notes:

1. The Startup node in this file contains the settings for the rst3
   command. If you use sphinx, **set @bool rst3_call_docutils = False**.
   
2. Leo will not create ~/myDocument.html automatically. Only the rst3
   command does that.
   
3. Executing the make-sphinx command will do everything needed to make
   myDocument.html. The @button make-sphinx node (a child of the Startup
   node) creates the make-sphinx command.
   
4. The node myDocument.html.txt is the intermediate file produced by the
   rst3 command.
</t>
<t tx="maphew.20140920000632.1682">#############
War and Peace
#############

        by Leo Tolstoy/Tolstoi
        
        BOOK ONE: 1805
</t>
<t tx="maphew.20140920000632.1683">"Well, Prince, so Genoa and Lucca are now just family estates of the
Buonapartes. But I warn you, if you don't tell me that this means war, if
you still try to defend the infamies and horrors perpetrated by that
Antichrist--I really believe he is Antichrist--I will have nothing more to
do with you and you are no longer my friend, no longer my 'faithful slave',
as you call yourself! But how do you do? I see I have frightened you--sit
down and tell me all the news."

It was in July, 1805, and the speaker was the well-known Anna Pavlovna
Scherer, maid of honor and favorite of the Empress Marya Fedorovna. With
these words she greeted Prince Vasili Kuragin, a man of high rank and
importance, who was the first to arrive at her reception. Anna Pavlovna had
had a cough for some days. She was, as she said, suffering from la grippe;
grippe being then a new word in St. Petersburg, used only by the elite.

...stuff happens...</t>
<t tx="maphew.20140920000632.1684">You can make whatever notes 
to yourself you like here, 
as these lines won't appear 
in the output files. :)

</t>
<t tx="maphew.20140920000632.1685">Neither this node nor any descendant node will appear in the output file.</t>
<t tx="maphew.20140920000632.1686">TL;DR

...la femme la plus seduisante de Petersbourg,* ...</t>
<t tx="maphew.20140920000632.1687">*The most fascinating woman in Petersburg.</t>
<t tx="maphew.20140920000632.1688">From the time the law of Copernicus was discovered and proved, the mere
recognition of the fact that it was not the sun but the earth that moves
sufficed to destroy the whole cosmography of the ancients.

...
</t>
<t tx="maphew.20140920000632.1689">..  and now we skip to the end of last chapter, while demonstrating use of an
..  organizer node (a node whose name does not appear in the output document),
..  and that rst comments appear as html comments (try 'View Source' on
..  output.html)

In the first case it was necessary to renounce the consciousness of an
unreal immobility in space and to recognize a motion we did not feel; in
the present case it is similarly necessary to renounce a freedom that does
not exist, and to recognize a dependence of which we are not conscious.
   
--- The End ---
</t>
<t tx="maphew.20140920000632.1690">.. rst3: filename: ~/myDocument.html

#############
War and Peace
#############

        by Leo Tolstoy/Tolstoi
        
        BOOK ONE: 1805

Chapter I
+++++++++

"Well, Prince, so Genoa and Lucca are now just family estates of the
Buonapartes. But I warn you, if you don't tell me that this means war,
if you still try to defend the infamies and horrors perpetrated by
that Antichrist--I really believe he is Antichrist--I will have
nothing more to do with you and you are no longer my friend, no longer
my 'faithful slave,' as you call yourself! But how do you do? I see
I have frightened you--sit down and tell me all the news."

...stuff happens...

Chapter XII
+++++++++++

From the time the law of Copernicus was discovered and proved, the
mere recognition of the fact that it was not the sun but the earth
that moves sufficed to destroy the whole cosmography of the
ancients.

...

.. and now we skip to the end of last chapter, while demonstrating use of an
    organizer node (a node whose name does not appear in the output document),
    and that rst comments appear as html comments (try 'View Source' on
    output.html)

In the first case it was necessary to renounce the consciousness
of an unreal immobility in space and to recognize a motion we did
not feel; in the present case it is similarly necessary to renounce
a freedom that does not exist, and to recognize a dependence of
which we are not conscious.
   
--- The End ---

</t>
<t tx="maphew.20140920000632.1691"></t>
<t tx="maphew.20140920004020.1708"></t>
<t tx="maphew.20140922213912.1720">@language python</t>
<t tx="maphew.20140922213912.1721"></t>
<t tx="maphew.20140927120559.1738"></t>
<t tx="maphew.20140927121126.1732"></t>
<t tx="maphew.20140927121126.1733">gnx: maphew.20140927121126.1730
</t>
<t tx="maphew.20140927121126.1735">gnx: maphew.20140927121126.1731
unl: setup declarations
</t>
<t tx="maphew.20140927121126.1737">gnx: maphew.20140927121126.1736
</t>
<t tx="maphew.20140927121126.1789">''' Sample of installed.db.

    package_name    archive_filename    [?]  
'''
@killcolor

INSTALLED.DB 2
libxml2 libxml2-2.9.1-1.tar.bz2 0
gdal110dll gdal110dll-1.10.1-1.tar.bz2 0
libtiff libtiff-4.0.2-2.tar.bz2 0
libjpeg12 libjpeg12-6b-3.tar.bz2 0
python-core python-core-2.7.4-3.tar.bz2 0
netcdf netcdf-3.6.1-1.tar.bz2 0
freexl freexl-1.0.0e-1.tar.bz2 0
curl curl-7.15.1-2.tar.bz2 0
msvcrt msvcrt-1.0.1-12.tar.bz2 0
iconv iconv-1.9.1-1.tar.bz2 0
sip sip-4.12.1-4.tar.bz2 0
libpq libpq-8.3.10-3.tar.bz2 0
geos geos-3.4.2-1.tar.bz2 0
libintl libintl-0.14.4-2.tar.bz2 0
spatialite spatialite-4.1.1-1.tar.bz2 0
spatialite3dll spatialite-3.0.1-0.tar.bz2 0
libmysql libmysql-5.0.18-1.tar.bz2 0
sqlite3 sqlite3-3.7.17-1.tar.bz2 0
python-help python-help-2.7.4-1.tar.bz2 0
proj proj-4.8.0-0.tar.bz2 0
shell shell-1.0.0-13.tar.bz2 0
python python-2.7.4-2.tar.bz2 0
xerces-c xerces-c-2.7.0-1.tar.bz2 0
qt4-libs qt4-libs-4.7.1-6.tar.bz2 0
pyqt4 pyqt4-4.8.3-2.tar.bz2 0
proj-hpgn proj-hpgn-1.0-1.tar.bz2 0
python-tools python-tools-2.7.4-1.tar.bz2 0
gdal19dll gdal19dll-1.9.2-1.tar.bz2 0
openjpeg openjpeg-2.0.0-1.tar.bz2 0
gdal gdal-1.11.0-2.tar.bz2 0
msys msys-1.0.18-7.tar.bz2 0
xerces-c-vc9 xerces-c-vc9-3.1.1-2.tar.bz2 0
gdal18dll gdal-1.8.1-0.tar.bz2 0
ogdi ogdi-3.2.0b1-4.tar.bz2 0
python-testsuite python-testsuite-2.7.4-1.tar.bz2 0
hdf4 hdf4-4.2.0r3-4.tar.bz2 0
hdf5 hdf5-1.8.11-1.tar.bz2 0
libjpeg libjpeg-6b-5.tar.bz2 0
proj-datumgrid proj-datumgrid-1.5-1.tar.bz2 0
setup setup-1.0.7-10.tar.bz2 0
zlib zlib-1.2.3-1.tar.bz2 0
gdal15dll gdal-1.5.4-1.tar.bz2 0
szip szip-2.1-1.tar.bz2 0
python-tcltk python-tcltk-2.7.4-1.tar.bz2 0
openssl openssl-1.0.1g-1.tar.bz2 0
libgeotiff libgeotiff-1.3.0-3.tar.bz2 0
expat expat-2.0.1-1.tar.bz2 0
</t>
<t tx="maphew.20140927121126.1825">gnx: maphew.20140927121126.1742
unl: dapt declarations
gnx: maphew.20140927121126.1754
unl: get_config
gnx: maphew.20140927121126.1759
unl: setup
gnx: maphew.20140927121126.1791
unl: get installed
gnx: maphew.20140927121126.1778
unl: write installed
gnx: maphew.20140927121126.1755
unl: main
</t>
</tnodes>
</leo_file>

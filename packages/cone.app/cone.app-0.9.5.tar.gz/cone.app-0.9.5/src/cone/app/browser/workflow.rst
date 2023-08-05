Workflow dropdown
=================

::

    >>> from cone.tile import render_tile
    >>> from cone.app import root
    >>> from cone.app.testing.mock import (
    ...     WorkflowNode,
    ...     InexistentWorkflowNode,
    ... )
    >>> import cone.app.browser.workflow
    
    >>> request = layer.new_request()
    >>> node = WorkflowNode()
    
    >>> node.state
    u'initial'
    
    >>> layer.login('manager')
    
    >>> res = render_tile(node, request, 'wf_dropdown')
    >>> res.find('title="Change state">initial</a>') > -1
    True
    
    >>> request.params['do_transition'] = 'initial_2_final'
    >>> res = render_tile(node, request, 'wf_dropdown')
    >>> res.find('class="state-final">final</span>') > -1
    True
    
    >>> node.state
    u'final'
    
    >>> node = InexistentWorkflowNode()
    >>> request = layer.new_request()
    >>> render_tile(node, request, 'wf_dropdown')
    u'\n  \n'
    
    >>> layer.logout()
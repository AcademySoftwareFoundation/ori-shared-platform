"""
Delegate Manager
================

========
Overview
========
RPA is driven by a powerful delegate manager, which makes it easy to observe and respond to any method invoked by the user.
Rather than relying on PySide signals for each method, users can simply attach a pre or post delegate to react to user interactions. This streamlines the workflow and provides a flexible, centralized way to handle behavior across the system.

=====================
Why Delegate Manager?
=====================
Having a Delegate Manager per RPA module enables RPA users to,

1. Add the core delegate to each RPA methods
2. Set permissions on each of the RPA methods
3. Listen to any RPA method calls and decorate them with callables that will be called before or after the core delegate is called.

===================
What is a Delegate?
===================
A delegate is any Python callable that needs to be called when an RPA method
is called.

=============================
What is the delegate-manager?
=============================
Every RPA module has a delegate manager. When a particular method of an RPA
module is called, it will use it's module's delegate manager to call all the
delegates that are associated with the method.

===================
Types of Delegates:
===================
Following are the 4 types of delegates that any RPA method can have. And the
delegates will be called in the following order as well.

1. Permission Delegates
2. Pre Delegates
3. Core Delegate
4. Post Delegates

Permission Delegates:
---------------------
An RPA method can have 0 or more permission delegates. In order for the
Pre Delegates, Core Delegate and Post Delegates of a given method to be
called, all the Permission Delegates of a given method needs to return True.
Note that the given delegate(callable) will be receiving the same args and
kwargs that are passed to the rpa_method.

Note that the given delegate(callable) will be receiving the same args and
kwargs that are passed to the rpa_method as its inputs.
Hence signature of the callable should look like this,

.. code-block:: python

    def permission_delegate(self, *args, **kwargs):
        pass

Instead of \*args and \**kwargs you can have the actual args and kwargs
based on the rpa_method.

Pre Delegates:
--------------
An RPA method can have 0 or more pre delegates. These are the delegates that
get called before the core delegate is called. Note that the given
delegate(callable) will be receiving the same args and kwargs that are passed
to the rpa_method.

Note that the given delegate(callable) will be receiving the same args and
kwargs that are passed to the rpa_method as its inputs.
Hence signature of the callable should look like this,

.. code-block:: python

    def pre_delegate(self, *args, **kwargs):
        pass

Instead of \*args and \**kwargs you can have the actual args and kwargs
based on the rpa_method.

Core Delegate:
--------------
An RPA method can have 0 or 1 core delegate. This is the actual delegate that
needs to be called when the user calls the RPA method. The output of this
delegate is what is returned back to the called of the RPA method. If no
delegate is present for a RPA method then None will be returned.

Post Delegates:
---------------
An RPA method can have 0 or more post delegates. These are the
delegates that get called after the core delegate is called.

Note that the given delegate(callable) will be receiving the output of
the main delegate as it's first argument and the same args and kwargs
that are passed to the rpa_method as the subsequent inputs.
Hence signature of the callable should look like this,

.. code-block:: python

    def post_delegate(self, out, *args, **kwargs):
        pass

Instead of \*args and \**kwargs you can have the actual args and kwargs
based on the rpa_method.
"""

from typing import Any, Callable, Optional, List, Dict


class DelegateMngr:
    def __init__(self, logger):
        self.__logger = logger
        self.__permission_delegates = {}
        self.__pre_delegates = {}
        self.__core_delegates = {}
        self.__post_delegates = {}

    def add_permission_delegate(
        self, rpa_method:Callable, delegate:Callable)->None:
        """
        An RPA method can have 0 or more permission delegates. In order for
        the Pre Delegates, Core Delegate and Post Delegates of a given method
        to be called, all the Permission Delegates of a given method needs to
        return True. Note that the given delegate(callable) will be receiving
        the same args and kwargs that are passed to the rpa_method.

        Note that the given delegate(callable) will be receiving the same args
        and kwargs that are passed to the rpa_method as its inputs.
        Hence signature of the callable should look like this,

        .. code-block:: python

            def permission_delegate(self, *args, **kwargs):
                pass

        Instead of \*args and \**kwargs you can have the actual args and kwargs
        based on the rpa_method.

        Args:
            rpa_method (callable):
                A method of an RPA module

            delegate (callable):
                Callable that returns a boolean value of True or False.
        Returns:
            None
        """
        self.__permission_delegates.setdefault(
            rpa_method, []).append(delegate)

    def get_permission_delegates(self, rpa_method:Callable)->List[Callable]:
        """
        Get list of all permission-delegates of the given rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            None
        """
        return self.__permission_delegates.get(rpa_method, [])

    def remove_permission_delegate(
        self, rpa_method:Callable, delegate:Callable)->None:
        """
        Remove the given deletegate as a permission delegate for the given
        rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module

            delegate (callable):
                Callable that was previously set as a permission delegate
                of the given rpa_method.
        Returns:
            None
        """
        try:
            self.__permission_delegates.setdefault(
                rpa_method, []).remove(delegate)
        except ValueError: pass

    def clear_permission_delegates(self, rpa_method:Callable)->None:
        """
        Clears all permission delegates for the given rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            None
        """
        self.__permission_delegates.setdefault(rpa_method, []).clear()

    def add_pre_delegate(
        self, rpa_method:Callable, delegate:Callable)->None:
        """
        An RPA method can have 0 or more pre delegates. These are the
        delegates that get called before the core delegate is called.
        Note that the given delegate(callable) will be receiving the same
        args and kwargs that are passed to the rpa_method.

        Note that the given delegate(callable) will be receiving the same
        args and kwargs that are passed to the rpa_method as its inputs.
        Hence signature of the callable should look like this,

        .. code-block:: python

            def pre_delegate(self, *args, **kwargs):
                pass

        Instead of \*args and \**kwargs you can have the actual args and kwargs
        based on the rpa_method.

        Args:
            rpa_method (callable):
                A method of an RPA module

            delegate (callable):
                Callable that needs to be called before core delegate
        Returns:
            None
        """
        self.__pre_delegates.setdefault(rpa_method, []).append(delegate)

    def get_pre_delegates(self, rpa_method:Callable)->List[Callable]:
        """
        Get list of all pre-delegates of the given rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            None
        """
        return self.__pre_delegates.get(rpa_method, [])

    def remove_pre_delegate(
        self, rpa_method:Callable, delegate:Callable)->None:
        """
        Remove the given deletegate as a pre delegate for the given
        rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module

            delegate (callable):
                Callable that was previously set as a pre delegate
                of the given rpa_method.
        Returns:
            None
        """
        try:
            self.__pre_delegates.setdefault(
                rpa_method, []).remove(delegate)
        except ValueError: pass

    def clear_pre_delegates(self, rpa_method:Callable)->None:
        """
        Clears all pre delegates for the given rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            None
        """
        self.__pre_delegates.setdefault(rpa_method, []).clear()

    def _set_core_delegate(
        self, rpa_method:Callable, delegate:Callable)->None:
        """
        An RPA method can have 0 or 1 core delegate. This is the actual
        delegate that needs to be called when the user calls the RPA method.
        The output of this delegate is what is returned back to the called of
        the RPA method. If no delegate is present for a RPA method then None
        will be returned.

        This method must be used with caution as it sets the core callable
        that will be called when the given rpa_method is called.

        Args:
            rpa_method (callable):
                A method of an RPA module

            delegate (callable):
                Callable that needs to be called when rpa_method is called.
                The value returned by this callable will be returned back
                to the caller.
        Returns:
            None
        """
        self.__core_delegates[rpa_method] = delegate

    def _get_core_delegate(self, rpa_method:Callable)->Optional[Callable]:
        """
        Get the core delegate that has been set for the given rpa_method

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            Optional[Callable]:
            Core delegate of given rpa_method if available otherwise None
        """
        return self.__core_delegates.get(rpa_method)

    def _remove_core_delegate(self, rpa_method:Callable)->None:
        """
        Remove the core delegate that was previously set to the given
        rpa_method.

        This method must be used with caution as it removes the core callable
        that will be called when the given rpa_method is called.

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            None
        """
        self.__core_delegates.pop(rpa_method, None)

    def add_post_delegate(
        self, rpa_method:Callable, delegate:Callable)->None:
        """
        An RPA method can have 0 or more post delegates. These are the
        delegates that get called after the core delegate is called.

        Note that the given delegate(callable) will be receiving the output of
        the main delegate as it's first argument and the same args and kwargs
        that are passed to the rpa_method as the subsequent inputs.
        Hence signature of the callable should look like this,

        .. code-block:: python

            def post_delegate(self, out, *args, **kwargs):
                pass

        Instead of \*args and \**kwargs you can have the actual args and kwargs
        based on the rpa_method.

        Args:
            rpa_method (callable):
                A method of an RPA module

            delegate (callable):
                Callable that needs to be called after core delegate
        Returns:
            None
        """
        self.__post_delegates.setdefault(rpa_method, []).append(delegate)

    def get_post_delegates(self, rpa_method:Callable)->List[Callable]:
        """
        Get list of all post-delegates of the given rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            None
        """
        return self.__post_delegates.get(rpa_method, [])

    def remove_post_delegate(
        self, rpa_method:Callable, delegate:Callable)->None:
        """
        Remove the given deletegate as a post delegate for the given
        rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module

            delegate (callable):
                Callable that was previously set as a post delegate
                of the given rpa_method.
        Returns:
            None
        """
        try:
            self.__post_delegates.setdefault(
                rpa_method, []).remove(delegate)
        except ValueError: pass

    def clear_post_delegates(self, rpa_method:Callable)->None:
        """
        Clears all post delegates for the given rpa method.

        Args:
            rpa_method (callable):
                A method of an RPA module
        Returns:
            None
        """
        self.__post_delegates.setdefault(rpa_method, []).clear()

    def call(
        self, rpa_method:Callable,
        args:Optional[List]=None, kwargs:Optional[Dict]=None)->Any:
        """
        Call all the delegates associated with the given rpa_method with
        the provided args and kwargs.

        Args:
            rpa_method (callable):
                A method of an RPA module

            args (List[Any]):
                List of arguments to the passed to the delegates

            kwargs (Dict):
                Dict of key-word arguments to the passed to the delegates

        Returns:
            (Any): Value returned by core delegate callable
        """
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        if not self.__core_delegates.get(rpa_method):
            self.__logger.warning(
                f"API method does not have core delegate! {rpa_method}")
            out = None
        elif self.__is_allowed(rpa_method, args, kwargs):
            self.__call_pre_delegates(rpa_method, args, kwargs)
            out = self.__core_delegates[rpa_method](*args, **kwargs)
            self.__call_post_delegates(rpa_method, out, args, kwargs)
        else:
            self.__logger.warning(
                f"Permission not available to call this API method! {rpa_method}")
            out = None
        return out

    def __is_allowed(self, rpa_method, args, kwargs):
        permission_delegates = self.__permission_delegates.get(rpa_method)
        if permission_delegates:
            is_allowed = all([permission_delegate(*args, **kwargs) \
                for permission_delegate in permission_delegates])
        else: is_allowed = True
        return is_allowed

    def __call_pre_delegates(self, rpa_method, args, kwargs):
        for delegate in self.__pre_delegates.get(rpa_method, []):
            delegate(*args, **kwargs)

    def __call_post_delegates(self, rpa_method, out, args, kwargs):
        for delegate in self.__post_delegates.get(rpa_method, []):
            delegate(out, *args, **kwargs)

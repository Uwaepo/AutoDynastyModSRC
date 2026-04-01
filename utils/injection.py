import inspect
from functools import wraps

# Injection function was taken and adapted from TURBODRIVER.

# This function overrides an existing Sims 4 method to add additional code or to bypass running the original all-together.

# Original source: https://gist.github.com/TURBODRIVER/8bd0d1194be179a1309496c730b5b188

# **PARAMETERS**
# target_object: The Sims 4 Class/Module that contains the function you wish to override.
# target_function_name: The name of the function you wish to override.
# safe: A flag to catch non existent functions from being passed.

def inject_to(target_object, target_function_name, safe=False):
    # Safe block to catch non-existent functions if safe mode is on. Returns itself if True and there is no function.
    if safe and not hasattr(target_object, target_function_name):
        # Wraps itself.
        def _self_wrap(wrap_function):
            return wrap_function
        
        # Returns itself in a wrapped function.
        return _self_wrap

    # Wraps the new and original function in a decorator which will replace the function on the original object.
    def _wrap_original_function(original_function, new_function):
        # functools.wraps automatically wraps the original function in a decorator and copies it's attributes.
        @wraps(original_function)

        # The decorator function to wrap itself in.
        def _wrapped_function(*args, **kwargs):

            # Checks if the original_function is a property or a function/method.
            if type(original_function) is property:
                # Resolves the property value to it's original function, which is what gets overriden.
                return new_function(original_function.fget, *args, **kwargs)
            else:
                # Original_function is assumed to be a function. New function takes it's place.
                return new_function(original_function, *args, **kwargs)

        # Checks if the original function is a method.
        # If so, converts the wrapped function into a bound method within the same instance as the original.
        # This is what links the wrapped function to the original object, and allows self to be passed to the new function.
        if inspect.ismethod(original_function):
            # Checks that the original function has a self attribute, making it a bound method.
            if hasattr(original_function, '__self__'):
                # Turns the wrapped function into a bound method with the same attributes as the original and returns it.
                return _wrapped_function.__get__(original_function.__self__, original_function.__self__.__class__)

            # If the function is not a bound method, it is returned as a class method bound to original class. (NOT object)
            return classmethod(_wrapped_function)
        # Checks if the original_function is a property if it is not a method.
        elif type(original_function) is property:
            # Returns the _wrapped_function as a property where it's return value can be resolved.
            return property(_wrapped_function)
        else:
            # Returns itself if the original_function is neither a class/bound method or a property.
            return _wrapped_function

    # The injector function which calls the function wrapper.
    def _injected(wrap_function):
        # Gets the original function's attribute from the targeted object by name.
        original_function = getattr(target_object, target_function_name)
        # Calls the wrapper function to return the new function inside of a decorator with the same attributes as the original_function.
        # This wrapped function then overrides the original function's attribute, so it is run in it's place.
        # The original function is passed as a parameter so that it can be ran by the new function.
        setattr(target_object, target_function_name, _wrap_original_function(original_function, wrap_function))

        return wrap_function

    return _injected

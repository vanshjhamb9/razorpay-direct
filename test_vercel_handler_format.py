"""
Test different handler formats to find what Vercel accepts
Run this locally to test handler formats
"""

import json

# Test different handler formats
def handler_function(request):
    """Function handler"""
    return {'statusCode': 200, 'body': 'OK'}

class HandlerClass:
    """Class handler"""
    def __call__(self, request):
        return {'statusCode': 200, 'body': 'OK'}

# Test which one works
print("Testing handler formats:")
print(f"1. Function handler type: {type(handler_function)}")
print(f"   Is callable: {callable(handler_function)}")
print(f"   Is class: {isinstance(handler_function, type)}")

handler_instance = HandlerClass()
print(f"2. Class handler type: {type(handler_instance)}")
print(f"   Is callable: {callable(handler_instance)}")
print(f"   Is class: {isinstance(handler_instance, type)}")

# Check what Vercel's error is looking for
from http.server import BaseHTTPRequestHandler
print(f"\nBaseHTTPRequestHandler: {BaseHTTPRequestHandler}")
print(f"HandlerClass is subclass: {issubclass(HandlerClass, BaseHTTPRequestHandler)}")

# The error says it's checking issubclass(base, BaseHTTPRequestHandler)
# So Vercel expects 'base' to be a class, not an instance or function


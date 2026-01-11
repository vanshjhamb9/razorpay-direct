# Debug Hypotheses - Vercel Handler TypeError

## Hypotheses Generated

### Hypothesis A: Handler Function Format Issue
**Theory:** Vercel expects handler to be a class, not a function
**Test:** Log handler type and see if Vercel accepts function handlers
**Instrumentation:** Log handler type, callability, name at module level

### Hypothesis B: Import Time Error
**Theory:** Error happens during module import, not runtime
**Test:** Check if error occurs before handler is even called
**Instrumentation:** Log at module load start, after imports, at handler definition

### Hypothesis C: Vercel Python Runtime Version Issue
**Theory:** @vercel/python builder version incompatible with function handlers
**Test:** Check if we need different builder or configuration
**Instrumentation:** Log Python version, Vercel builder version

### Hypothesis D: Import from main.py Causes Issue
**Theory:** Importing from main.py (which has Flask) causes Vercel to detect Flask and fail
**Test:** Check if import succeeds or fails
**Instrumentation:** Log import success/failure

### Hypothesis E: Request Object Format Wrong
**Theory:** Vercel passes request in different format than expected
**Test:** Log request type and attributes
**Instrumentation:** Log request type, available attributes

### Hypothesis F: Handler Not Being Called
**Theory:** Error happens before handler is called, during Vercel's inspection
**Test:** Check if handler function is ever executed
**Instrumentation:** Log at handler function entry

### Hypothesis G: Exception Handling Issue
**Theory:** Exceptions not being caught properly
**Test:** Log all exceptions
**Instrumentation:** Log exception type and message

### Hypothesis H: Module Export Format
**Theory:** Handler needs to be exported differently (not as function)
**Test:** Check handler type at module level
**Instrumentation:** Log handler type after definition

## Next Steps

1. Deploy with instrumentation
2. Test webhook
3. Read logs from .cursor/debug.log
4. Analyze which hypothesis is confirmed
5. Fix based on evidence




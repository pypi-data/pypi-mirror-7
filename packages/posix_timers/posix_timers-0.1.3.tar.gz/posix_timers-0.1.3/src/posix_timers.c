#include <Python.h>
#include <structseq.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>


static PyObject *ptimers_timespec_as_rational(const struct timespec *spec);
static void ptimers_notify_trampoline(union sigval sigev_value);
static PyObject *ptimers_struct_itimerspec(const struct itimerspec *spec);

typedef struct {
    PyObject_HEAD
    clockid_t clk_id;
} ptimers_ClockObject;

static PyTypeObject ptimers_ClockType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "posix_timers.Clock",      /*tp_name*/
    sizeof(ptimers_ClockObject), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Identifies a posix clock.",   /*tp_doc*/
};

typedef struct {
    PyObject_HEAD
    timer_t     timer_id;
    PyObject    *notify;
} ptimers_TimerObject;

static PyTypeObject ptimers_TimerType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "posix_timers.Timer",      /*tp_name*/
    sizeof(ptimers_TimerObject), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Identifies a posix timer.",   /*tp_doc*/
};

static PyTypeObject struct_itimerspec_type;

static PyStructSequence_Field struct_itimerspec_fields[] = {
    {"interval",   "Periodic expiration in seconds, 0 if disabled."},
    {"value",      "Time to next expiration in seconds, 0 if disabled."},
    {0}
};

static PyStructSequence_Desc struct_itimerspec_desc = {
    "posix_timers.itimerspec",
    "Current timer expiration status as pair of interval and time to next\n"
    "expiration.",
    struct_itimerspec_fields,
    2,
};


static PyObject *
ptimers_Clock_get_clk_id(ptimers_ClockObject *self, void *closure)
{
    return PyLong_FromLongLong(self->clk_id);
}

static PyObject *
ptimers_Clock_get_resolution(ptimers_ClockObject *self, void *closure)
{
    struct timespec resolution;

    if (clock_getres(self->clk_id, &resolution) == -1)
        return PyErr_SetFromErrno(PyExc_OSError);

    return ptimers_timespec_as_rational(&resolution);
}

static PyObject *
ptimers_clock_getres(PyObject *self, PyObject *args)
{
    ptimers_ClockObject *clock_object;

    if (!PyArg_ParseTuple(args, "O!:clock_getres", &ptimers_ClockType, &clock_object))
        return NULL;

    return ptimers_Clock_get_resolution(clock_object, NULL);
}

static PyObject *
ptimers_Clock_get_time(ptimers_ClockObject *self, void *closure)
{
    struct timespec result;

    if (clock_gettime(self->clk_id, &result) == -1)
        return PyErr_SetFromErrno(PyExc_OSError);

    return ptimers_timespec_as_rational(&result);
}

static PyObject *
ptimers_clock_gettime(PyObject *self, PyObject *args)
{
    ptimers_ClockObject *clock_object;

    if (!PyArg_ParseTuple(args, "O!:clock_gettime", &ptimers_ClockType, &clock_object))
        return NULL;

    return ptimers_Clock_get_time(clock_object, NULL);
}

static PyObject *
ptimers_timer_create(PyObject *self, PyObject *args)
{
    ptimers_ClockObject *clock_object;
    ptimers_TimerObject *timer_object = NULL;
    PyObject *notify = NULL;
    struct sigevent ev;
    int rc;

    if (!PyArg_ParseTuple(args, "O!|O:timer_create",
            &ptimers_ClockType, &clock_object, &notify))
        return NULL;

    if (notify) {
        if (! PyCallable_Check(notify)) {
            PyErr_SetString(PyExc_TypeError, "notify must be None or callable");
            return NULL;
        }
    }

    timer_object = (ptimers_TimerObject *) PyType_GenericAlloc(&ptimers_TimerType, 0);
    if (! timer_object)
        return NULL;

    if (notify) {
        ev.sigev_notify = SIGEV_THREAD;
        ev.sigev_signo = 0;
        Py_INCREF(notify);
        timer_object->notify = notify;
        ev.sigev_value.sival_ptr = (void *) notify;
        ev.sigev_notify_function = ptimers_notify_trampoline;
        ev.sigev_notify_attributes = NULL;
    } else {
        ev.sigev_notify = SIGEV_NONE;
    }

    rc = timer_create(clock_object->clk_id, &ev, &timer_object->timer_id);
    if (rc < 0) {
        Py_DECREF(timer_object);
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    return (PyObject *) timer_object;
}

static PyObject *
ptimers_get_thread_cpuclock(PyObject *self, PyObject *args)
{
    PyObject *thread_object = NULL, *ident_object = NULL;
    pthread_t thread_id;
    clockid_t clk_id;
    ptimers_ClockObject *clock = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "O:get_thread_cpuclock", &thread_object))
        return NULL;

    if (PyObject_HasAttrString(thread_object, "ident")) {
        ident_object = PyObject_GetAttrString(thread_object, "ident");
        if (!ident_object)
            return NULL;
    } else {
        ident_object = thread_object;
    }

    if (PyInt_Check(ident_object))
        thread_id = PyInt_AS_LONG(ident_object);
    else if (PyLong_Check(ident_object)) {
        thread_id = PyLong_AsUnsignedLongLong(ident_object);
        if (PyErr_Occurred())
            return NULL;
    } else {
        return PyErr_Format(PyExc_TypeError, "get_thread_cpuclock: threading.Thread or int required.");
    }

    err = pthread_getcpuclockid(thread_id, &clk_id);
    if (err)
        return PyErr_SetFromErrno(PyExc_OSError);

    clock = (ptimers_ClockObject *) PyType_GenericAlloc(&ptimers_ClockType, 0);
    if (clock)
        clock->clk_id = clk_id;
    return (PyObject *) clock;
}


static PyObject *
ptimers_timer_gettime(PyObject *self, PyObject *args)
{
    ptimers_TimerObject *timer_object = (ptimers_TimerObject*) self;
    struct itimerspec curr_value;

    if (!PyArg_ParseTuple(args, ":gettime"))
        return NULL;

    if (timer_gettime(timer_object->timer_id, &curr_value) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    return ptimers_struct_itimerspec(&curr_value);
}

static PyObject *
ptimers_timer_settime(ptimers_TimerObject *self, PyObject *args, PyObject *kwds)
{
    int flags = 0;
    double interval = 0, value = 0;
    struct itimerspec new_spec, old_spec;
    char *kwlist[] = {"flags", "interval", "value", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|idd:settime", kwlist,
            &flags, &interval, &value))
        return NULL;

    new_spec.it_interval.tv_sec  = (long) interval;
    new_spec.it_interval.tv_nsec = (long) (fmod(interval, 1.0) * 1e9);
    new_spec.it_value.tv_sec     = (long) value;
    new_spec.it_value.tv_nsec    = (long) (fmod(value, 1.0) * 1e9);

    if (timer_settime(self->timer_id, flags, &new_spec, &old_spec) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    return ptimers_struct_itimerspec(&old_spec);
}

static PyObject *
ptimers_struct_itimerspec(const struct itimerspec *spec)
{
    PyObject *result, *t;

    result = PyStructSequence_New(&struct_itimerspec_type);

    if (result) {
        t = ptimers_timespec_as_rational(&spec->it_interval);
        if (!t)
            goto error_out;
        PyStructSequence_SET_ITEM(result, 0, t);

        t = ptimers_timespec_as_rational(&spec->it_value);
        if (!t)
            goto error_out;
        PyStructSequence_SET_ITEM(result, 1, t);
    }
    return result;

error_out:
    Py_DECREF(result);
    return NULL;
}

static void ptimers_notify_trampoline(union sigval sigev_value)
{
    PyObject *r;
    PyObject *callable = (PyObject *) sigev_value.sival_ptr;
    PyGILState_STATE gilstate;

    gilstate = PyGILState_Ensure();
    r = PyObject_CallFunction(callable, NULL);
    if (r) {
        Py_DECREF(r);
    } else {
        PyErr_WriteUnraisable(NULL);
    }
    PyGILState_Release(gilstate);
}

static PyObject *
ptimers_timespec_as_rational(const struct timespec *spec)
{
    double value = spec->tv_sec + spec->tv_nsec * 1e-9;
    return PyFloat_FromDouble(value);
}

static PyObject *
ptimers_Clock_new(PyTypeObject *subtype, PyObject *args, PyObject *kwds)
{
    ptimers_ClockObject *clock = NULL;
    long long clk_id_value = 0;
    clockid_t clk_id;

    if (!PyArg_ParseTuple(args, "L:Clock", &clk_id_value))
        return NULL;

    clk_id = (clockid_t) clk_id_value;

    clock = (ptimers_ClockObject *) PyType_GenericAlloc(&ptimers_ClockType, 0);
    if (clock)
        clock->clk_id = clk_id;
    return (PyObject *) clock;
}

int
ptimers_add_clock(PyObject *module, const char *name, clockid_t clk_id)
{
    ptimers_ClockObject *clock = (ptimers_ClockObject *) PyType_GenericAlloc(&ptimers_ClockType, 0);
    if (! clock)
        return -1;
    clock->clk_id = clk_id;
    return PyModule_AddObject(module, name, (PyObject *) clock);
}

static PyGetSetDef ptimers_Clock_getsetdef[] = {
    {"clk_id",
        (getter) ptimers_Clock_get_clk_id, NULL,
        "Identifier of the clock as passed to POSIX clock_... functions.", NULL },
    {"resolution",
        (getter) ptimers_Clock_get_resolution, NULL,
        "Resolution of the clock in seconds.", NULL },
    {"time",
        (getter) ptimers_Clock_get_time, NULL,
        "Time of this clock in seconds.", NULL },
    { NULL }  /* Sentinel */
};


static PyMethodDef ptimers_Timer_methods[] = {
    { "gettime", ptimers_timer_gettime, METH_VARARGS,
        "gettime() -> (interval, value)\n"
        "Returns the current value of the timer and the interval for periodic"
        "expiration." },
    { "settime", (PyCFunction) ptimers_timer_settime, METH_VARARGS | METH_KEYWORDS,
        "settime(flags, interval, value) -> old (interval, value)\n"
        "Sets expiration interval and time to next expiration, returns old "
        "values." },
    { NULL, NULL, 0, NULL }
};

static PyMethodDef ptimers_methods[] = {
    { "clock_getres", ptimers_clock_getres, METH_VARARGS,
        "Find the resolution of a posix clock." },
    { "clock_gettime", ptimers_clock_gettime, METH_VARARGS,
        "Read the value of a posix clock." },
    { "timer_create", ptimers_timer_create, METH_VARARGS,
        "timer_create(clock, notify=None)\n"
        "Create a timer which call notify (w/o args) on expiration. notify \n"
        "can be None if no notification is required or any Python callable \n"
        "which will be called on a new thread (or as if on a new thread)." },
    { "get_thread_cpuclock", ptimers_get_thread_cpuclock, METH_VARARGS,
        "get_thread_cpuclock(thread)\n"
        "Create a Clock that measures the CPU time of the given thread. \n"
        "thread can be either an instance of threading.Thread or the thread \n"
        "identifier fro threading.Thread.ident." },
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initposix_timers(void)
{
    PyObject *module = NULL;

    ptimers_ClockType.tp_getset = ptimers_Clock_getsetdef;
    ptimers_ClockType.tp_new    = ptimers_Clock_new;
    if (PyType_Ready(&ptimers_ClockType) < 0)
        return;

    ptimers_TimerType.tp_methods = ptimers_Timer_methods;
    if (PyType_Ready(&ptimers_TimerType) < 0)
        return;

    PyStructSequence_InitType(&struct_itimerspec_type, &struct_itimerspec_desc);

    module = Py_InitModule3("posix_timers", ptimers_methods,
            "POSIX Timers API module");

#define ADD_CLOCK(name, clk_id) \
    if (ptimers_add_clock(module, name, clk_id) == -1) \
        return

    ADD_CLOCK("CLOCK_REALTIME", CLOCK_REALTIME);
    ADD_CLOCK("CLOCK_MONOTONIC", CLOCK_MONOTONIC);
    ADD_CLOCK("CLOCK_PROCESS_CPUTIME", CLOCK_PROCESS_CPUTIME_ID);
    ADD_CLOCK("CLOCK_THREAD_CPUTIME", CLOCK_THREAD_CPUTIME_ID );

    /* Linux specific clocks */

#if defined(CLOCK_MONOTONIC_RAW)
    /* Since Linux 2.6.28 */
    ADD_CLOCK("CLOCK_MONOTONIC_RAW", CLOCK_MONOTONIC_RAW);
#endif
#if defined(CLOCK_MONOTONIC_COARSE)
    /* Since Linux 2.6.32 */
    ADD_CLOCK("CLOCK_MONOTONIC_COARSE", CLOCK_MONOTONIC_COARSE);
#endif
#if defined(CLOCK_REALTIME_COARSE)
    /* Since Linux 2.6.32 */
    ADD_CLOCK("CLOCK_REALTIME_COARSE", CLOCK_REALTIME_COARSE);
#endif

    PyObject_SetAttrString(module, "Clock", (PyObject *) &ptimers_ClockType);
    PyObject_SetAttrString(module, "Timer", (PyObject *) &ptimers_TimerType);
    PyModule_AddIntMacro(module, TIMER_ABSTIME);
}

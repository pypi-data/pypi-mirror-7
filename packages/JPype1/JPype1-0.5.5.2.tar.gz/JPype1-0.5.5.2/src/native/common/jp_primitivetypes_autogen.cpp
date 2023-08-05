
/*****************************************************************************
   Copyright 2004-2008 Steve Menard
   
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
*****************************************************************************/   

// This code has been automatically generated ... No not edit

#include <Python.h>
#include <jpype.h>

#define CONVERSION_ERROR_HANDLE \
PyObject* exe = PyErr_Occurred(); \
if(exe != NULL) \
{\
	stringstream ss;\
	ss <<  "unable to convert element: " << PyObject_REPR(o) <<\
			" at index: " << i;\
	RAISE(JPypeException, ss.str());\
}

/**
 * TODO: document this
 */
// for python 2.6 we have also memory view available
#include <jpype_memory_view.h>
#include <typeinfo>
template <typename dtype>
inline bool
setViaBuffer(jarray array, int start, int length, PyObject* sequence) {
	// temporarily disabled until production stable
	return false;

#if (PY_VERSION_HEX >= 0x02070000)
	//creates a PyBuffer from sequence check for typeError,
	// if no underlying buff exists.
	PyObject* memview = PyMemoryView_FromObject(sequence);
	Py_buffer* buff = NULL;
	// check for TypeError, if no underlying buff exists.
	PyObject* err = PyErr_Occurred();
	if (not err) {
		buff = PyMemoryView_GET_BUFFER(memview);
		if (PyBuffer_IsContiguous(buff, 'C' )) {
			// TODO: ensure length of buffer contains enough elements somehow.
			assert((buff->len == length));
			jboolean isCopy;
			// TODO: impl for supported dtypes
			if (typeid(dtype) == typeid(double)) {
				jdoubleArray a = (jdoubleArray) array;
				jdouble* val = NULL;
				try {
					val = JPEnv::getJava()->GetDoubleArrayElements(a, &isCopy);
					val = (jdouble*) buff->buf; // TODO: test
					JPEnv::getJava()->ReleaseDoubleArrayElements(a,val, 0);
				} RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseDoubleArrayElements(a, val, JNI_ABORT); } );
			}
			else if(typeid(dtype) == typeid(float))
				JPEnv::getJava()->SetFloatArrayRegion(
						(jfloatArray)array, start, length, (jfloat*) buff->buf);
			else if(typeid(dtype) == typeid(int))
				JPEnv::getJava()->SetIntArrayRegion(
						(jintArray)array, start, length, (jint*) buff->buf);
			else if(typeid(dtype) == typeid(bool))
				JPEnv::getJava()->SetBooleanArrayRegion(
						(jbooleanArray)array, start, length, (jboolean*) buff->buf);
			else if(typeid(dtype) == typeid(char))
				JPEnv::getJava()->SetCharArrayRegion(
						(jcharArray)array, start, length, (jchar*) buff->buf);
			else if(typeid(dtype) == typeid(long))
				JPEnv::getJava()->SetLongArrayRegion(
						(jlongArray)array, start, length, (jlong*) buff->buf);
			else if(typeid(dtype) == typeid(jbyte)) // special case, lets use typedef for jbyte
				JPEnv::getJava()->SetByteArrayRegion(
						(jbyteArray)array, start, length, (jbyte*) buff->buf);
			else if(typeid(dtype) == typeid(short))
				JPEnv::getJava()->SetShortArrayRegion(
						(jshortArray)array, start, length, (jshort*) buff->buf);
			// deallocate memview
			Py_DECREF(memview);
			return true;
		}
	} else {
		PyErr_Clear();
	}
	return false;
#endif
}

jarray JPByteType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewByteArray(sz);
}

HostRef* JPByteType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.b = JPEnv::getJava()->GetStaticByteField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPByteType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.b = JPEnv::getJava()->GetByteField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPByteType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.b = JPEnv::getJava()->CallStaticByteMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPByteType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.b = JPEnv::getJava()->CallNonvirtualByteMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPByteType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jbyte val = convertToJava(obj).b;
    JPEnv::getJava()->SetStaticByteField(c, fid, val);
}

void JPByteType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jbyte val = convertToJava(obj).b;
    JPEnv::getJava()->SetByteField(c, fid, val);
}

vector<HostRef*> JPByteType::getArrayRange(jarray a, int start, int length)
{
    jbyteArray array = (jbyteArray)a;
    jbyte* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetByteArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.b = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseByteArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseByteArrayElements(array, val, JNI_ABORT); } );
}

void JPByteType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jbyteArray array = (jbyteArray)a;
    jbyte* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetByteArrayElements(array, &isCopy);
        
        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];
            
            val[start+i] = convertToJava(pv).b;            
        }
        JPEnv::getJava()->ReleaseByteArrayElements(array, val, 0);        
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseByteArrayElements(array, val, JNI_ABORT); } );
}

void JPByteType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{
	if(setViaBuffer<jbyte>(a, start, length, sequence))
		return;

    jbyteArray array = (jbyteArray)a;
    jbyte* val = NULL;
    jboolean isCopy;

	try {
		val = JPEnv::getJava()->GetByteArrayElements(array, &isCopy);
		for (Py_ssize_t i = 0; i < length; ++i) {
			PyObject* o = PySequence_GetItem(sequence, i);
			jbyte l = (jbyte) PyInt_AS_LONG(o);
			Py_DECREF(o);
			if(l == -1) { CONVERSION_ERROR_HANDLE; }
			val[start+i] = l;
		}
		JPEnv::getJava()->ReleaseByteArrayElements(array, val, 0);
	}
	RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseByteArrayElements(array, val, JNI_ABORT); } );
}

HostRef* JPByteType::getArrayItem(jarray a, int ndx)
{
    jbyteArray array = (jbyteArray)a;
    jbyte val;
    
    try {
        jvalue v;
        JPEnv::getJava()->GetByteArrayRegion(array, ndx, 1, &val);
        v.b = val;

        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPByteType::setArrayItem(jarray a, int ndx, HostRef* obj)
{
    jbyteArray array = (jbyteArray)a;
    
    try {
        jbyte val = convertToJava(obj).b;
        JPEnv::getJava()->SetByteArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}

PyObject* JPByteType::getArrayRangeToSequence(jarray a, int lo, int hi) {
    jbyteArray array = (jbyteArray)a;
    jbyte* val = NULL;
    jboolean isCopy;
    PyObject* res = NULL;

    try {
       val = JPEnv::getJava()->GetByteArrayElements(array, &isCopy);
       PyObject *tuple = PyTuple_New(hi - lo);

       for (Py_ssize_t i = lo; i < hi; i++)
           PyTuple_SET_ITEM(tuple, i, PyInt_FromLong(val[i]));

       JPEnv::getJava()->ReleaseByteArrayElements(array, val, JNI_ABORT);
       return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseByteArrayElements(array, val, JNI_ABORT); } );
}


//----------------------------------------------------------


jarray JPShortType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewShortArray(sz);
}

HostRef* JPShortType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.s = JPEnv::getJava()->GetStaticShortField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPShortType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.s = JPEnv::getJava()->GetShortField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPShortType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.s = JPEnv::getJava()->CallStaticShortMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPShortType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.s = JPEnv::getJava()->CallNonvirtualShortMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPShortType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jshort val = convertToJava(obj).s;
    JPEnv::getJava()->SetStaticShortField(c, fid, val);
}

void JPShortType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jshort val = convertToJava(obj).s;
    JPEnv::getJava()->SetShortField(c, fid, val);
}

vector<HostRef*> JPShortType::getArrayRange(jarray a, int start, int length)
{
    jshortArray array = (jshortArray)a;    
    jshort* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetShortArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.s = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseShortArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseShortArrayElements(array, val, JNI_ABORT); } );
}

void JPShortType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jshortArray array = (jshortArray)a;
    jshort* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetShortArrayElements(array, &isCopy);
        
        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];
            
            val[start+i] = convertToJava(pv).s;
        }
        JPEnv::getJava()->ReleaseShortArrayElements(array, val, 0);
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseShortArrayElements(array, val, JNI_ABORT); } );
}

void JPShortType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{
    if(setViaBuffer<short>(a, start, length, sequence))
    	return;

    jshortArray array = (jshortArray)a;
    jshort* val = NULL;
    jboolean isCopy;

	try {
		val = JPEnv::getJava()->GetShortArrayElements(array, &isCopy);
		for (Py_ssize_t i = 0; i < length; ++i) {
			PyObject* o = PySequence_GetItem(sequence, i);
			jshort l = (jshort) PyInt_AsLong(o);
			Py_DECREF(o);
			if(l == -1) { CONVERSION_ERROR_HANDLE; }
			val[start+i] = l;
		}
		JPEnv::getJava()->ReleaseShortArrayElements(array, val, 0);
	}
	RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseShortArrayElements(array, val, JNI_ABORT); } );

}

HostRef* JPShortType::getArrayItem(jarray a, int ndx)
{
    jshortArray array = (jshortArray)a;
    jshort val;
    
    try {
        JPEnv::getJava()->GetShortArrayRegion(array, ndx, 1, &val);
        jvalue v;
        v.s = val;

        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPShortType::setArrayItem(jarray a, int ndx , HostRef* obj)
{
    jshortArray array = (jshortArray)a;
    
    try {
        jshort val = convertToJava(obj).s;
        JPEnv::getJava()->SetShortArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}

PyObject* JPShortType::getArrayRangeToSequence(jarray a, int lo, int hi) {
    jshortArray array = (jshortArray)a;
    jshort* val = NULL;
    jboolean isCopy;
    PyObject* res = NULL;

    try {
       val = JPEnv::getJava()->GetShortArrayElements(array, &isCopy);
       res = PyList_New(hi - lo);
       for (Py_ssize_t i = lo; i < hi; i++)
         PyList_SET_ITEM(res, i - lo, PyInt_FromLong(val[i]));

       JPEnv::getJava()->ReleaseShortArrayElements(array, val, JNI_ABORT);
       return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseShortArrayElements(array, val, JNI_ABORT); } );
}

//----------------------------------------------------------


jarray JPIntType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewIntArray(sz);
}

HostRef* JPIntType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.i = JPEnv::getJava()->GetStaticIntField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPIntType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.i = JPEnv::getJava()->GetIntField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPIntType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.i = JPEnv::getJava()->CallStaticIntMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPIntType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.i = JPEnv::getJava()->CallNonvirtualIntMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPIntType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jint val = convertToJava(obj).i;
    JPEnv::getJava()->SetStaticIntField(c, fid, val);
}

void JPIntType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jint val = convertToJava(obj).i;
    JPEnv::getJava()->SetIntField(c, fid, val);
}

vector<HostRef*> JPIntType::getArrayRange(jarray a, int start, int length)
{
    jintArray array = (jintArray)a;
    jint* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetIntArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.i = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseIntArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseIntArrayElements(array, val, JNI_ABORT); } );
}

void JPIntType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jintArray array = (jintArray)a;    
    jint* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetIntArrayElements(array, &isCopy);
        
        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];
            
            val[start+i] = convertToJava(pv).i;            
        }
        JPEnv::getJava()->ReleaseIntArrayElements(array, val, 0);        
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseIntArrayElements(array, val, JNI_ABORT); } );
}

void JPIntType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{

	if(setViaBuffer<int>(a, start, length, sequence))
		return;

    jintArray array = (jintArray)a;
    jint* val = NULL;
    jboolean isCopy;

	try {
		val = JPEnv::getJava()->GetIntArrayElements(array, &isCopy);
		for (Py_ssize_t i = 0; i < length; ++i) {
			PyObject* o = PySequence_GetItem(sequence, i);
			jint v = (jint) PyInt_AsLong(o);
			Py_DecRef(o);
			if (v == -1) { CONVERSION_ERROR_HANDLE }
			val[start+i] = v;
		}
        JPEnv::getJava()->ReleaseIntArrayElements(array, val, 0);
	}
	RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseIntArrayElements(array, val, JNI_ABORT); } );
}

HostRef* JPIntType::getArrayItem(jarray a, int ndx)
{
    jintArray array = (jintArray)a;    
    jint val;
    
    try {
    	JPEnv::getJava()->GetIntArrayRegion(array, ndx, 1, &val);
        jvalue v;
        v.i = val;

        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPIntType::setArrayItem(jarray a, int ndx , HostRef* obj)
{
    jintArray array = (jintArray)a;    
    jint val;
    
    try {
        val = convertToJava(obj).i;
    	JPEnv::getJava()->SetIntArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}


PyObject* JPIntType::getArrayRangeToSequence(jarray a, int lo, int hi) {
	jintArray array = (jintArray)a;
    jint* val = NULL;
    jboolean isCopy;
    PyObject* res = NULL;
    try {
       val = JPEnv::getJava()->GetIntArrayElements(array, &isCopy);
       res = PyList_New(hi - lo);
       for (Py_ssize_t i = lo; i < hi; i++)
       {
         PyList_SET_ITEM(res, i - lo, PyInt_FromLong(val[i]));
       }
       JPEnv::getJava()->ReleaseIntArrayElements(array, val, JNI_ABORT);
       return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseIntArrayElements(array, val, JNI_ABORT); } );
}

//----------------------------------------------------------

jarray JPLongType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewLongArray(sz);
}

HostRef* JPLongType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.j = JPEnv::getJava()->GetStaticLongField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPLongType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.j = JPEnv::getJava()->GetLongField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPLongType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.j = JPEnv::getJava()->CallStaticLongMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPLongType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.j = JPEnv::getJava()->CallNonvirtualLongMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPLongType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jlong val = convertToJava(obj).j;
    JPEnv::getJava()->SetStaticLongField(c, fid, val);
}

void JPLongType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jlong val = convertToJava(obj).j;
    JPEnv::getJava()->SetLongField(c, fid, val);
}

vector<HostRef*> JPLongType::getArrayRange(jarray a, int start, int length)
{
    jlongArray array = (jlongArray)a;    
    jlong* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetLongArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.j = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseLongArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseLongArrayElements(array, val, JNI_ABORT); } );
}

void JPLongType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jlongArray array = (jlongArray)a;    
    jlong* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetLongArrayElements(array, &isCopy);
        
        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];
            
            val[start+i] = convertToJava(pv).j;            
        }
        JPEnv::getJava()->ReleaseLongArrayElements(array, val, 0);        
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseLongArrayElements(array, val, JNI_ABORT); } );
}

void JPLongType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{
    if(setViaBuffer<long>(a, start, length, sequence))
        return;

    jlongArray array = (jlongArray)a;
    jlong* val = NULL;
    jboolean isCopy;

	try {
		val = JPEnv::getJava()->GetLongArrayElements(array, &isCopy);
		for (Py_ssize_t i = 0; i < length; ++i) {
			PyObject* o = PySequence_GetItem(sequence, i);
			jlong l = (jlong) PyLong_AsLong(o);
			Py_DECREF(o);
			if(l == -1) { CONVERSION_ERROR_HANDLE; }
			val[start+i] = l;
		}
		JPEnv::getJava()->ReleaseLongArrayElements(array, val, 0);
	}
	RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseLongArrayElements(array, val, JNI_ABORT); } );
}



HostRef* JPLongType::getArrayItem(jarray a, int ndx)
{
    jlongArray array = (jlongArray)a;
    jlong val;
    
    try {
        JPEnv::getJava()->GetLongArrayRegion(array, ndx, 1, &val);
        jvalue v;
        v.j = val;
        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPLongType::setArrayItem(jarray a, int ndx , HostRef* obj)
{
    jlongArray array = (jlongArray)a;
    jlong val;
    
    try {
        val = convertToJava(obj).j;
        JPEnv::getJava()->SetLongArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}

PyObject* JPLongType::getArrayRangeToSequence(jarray a, int lo, int hi) {
    jlongArray array = (jlongArray)a;
    jlong* val = NULL;
    jboolean isCopy;
    PyObject* res = NULL;

    try {
       val = JPEnv::getJava()->GetLongArrayElements(array, &isCopy);
       res = PyList_New(hi - lo);
       for (Py_ssize_t i = lo; i < hi; i++)
         PyList_SET_ITEM(res, i - lo, PyLong_FromLong(val[i]));

       JPEnv::getJava()->ReleaseLongArrayElements(array, val, JNI_ABORT);
       return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseLongArrayElements(array, val, JNI_ABORT); } );
}


//----------------------------------------------------------


jarray JPFloatType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewFloatArray(sz);
}

HostRef* JPFloatType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.f = JPEnv::getJava()->GetStaticFloatField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPFloatType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.f = JPEnv::getJava()->GetFloatField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPFloatType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.f = JPEnv::getJava()->CallStaticFloatMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPFloatType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.f = JPEnv::getJava()->CallNonvirtualFloatMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPFloatType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jfloat val = convertToJava(obj).f;
    JPEnv::getJava()->SetStaticFloatField(c, fid, val);
}

void JPFloatType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jfloat val = convertToJava(obj).f;
    JPEnv::getJava()->SetFloatField(c, fid, val);
}

vector<HostRef*> JPFloatType::getArrayRange(jarray a, int start, int length)
{
    jfloatArray array = (jfloatArray)a;    
    jfloat* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetFloatArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.f = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseFloatArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseFloatArrayElements(array, val, JNI_ABORT); } );
}

void JPFloatType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jfloatArray array = (jfloatArray)a;    
    jfloat* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetFloatArrayElements(array, &isCopy);
        
        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];
            
            val[start+i] = convertToJava(pv).f;            
        }
        JPEnv::getJava()->ReleaseFloatArrayElements(array, val, 0);        
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseFloatArrayElements(array, val, JNI_ABORT); } );
}

void JPFloatType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{
    if(setViaBuffer<jfloat>(a, start, length, sequence))
        return;

	jfloatArray array = (jfloatArray)a;
	jfloat* val = NULL;
	jboolean isCopy;
	try {
		val = JPEnv::getJava()->GetFloatArrayElements(array, &isCopy);
		for (Py_ssize_t i = 0; i < length; ++i) {
			PyObject* o = PySequence_GetItem(sequence, i);
			jfloat v = (jfloat) PyFloat_AsDouble(o);
			Py_DecRef(o);
			if (v == -1.) { CONVERSION_ERROR_HANDLE; }
			val[start+i] = v;
		}
		JPEnv::getJava()->ReleaseFloatArrayElements(array, val, 0);
	}
	RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseFloatArrayElements(array, val, JNI_ABORT); } );
}

HostRef* JPFloatType::getArrayItem(jarray a, int ndx)
{
    jfloatArray array = (jfloatArray)a;
    jfloat val;
    
    try {
        JPEnv::getJava()->GetFloatArrayRegion(array, ndx, 1, &val);
        
        jvalue v;
        v.f = val;

        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPFloatType::setArrayItem(jarray a, int ndx , HostRef* obj)
{
    jfloatArray array = (jfloatArray)a;
    jfloat val;
    
    try {
        val = convertToJava(obj).f;
        JPEnv::getJava()->SetFloatArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}

PyObject* JPFloatType::getArrayRangeToSequence(jarray a, int lo, int hi) {
    jfloatArray array = (jfloatArray)a;
    jfloat* val = NULL;
    jboolean isCopy;
    PyObject* res = NULL;

    try {
       val = JPEnv::getJava()->GetFloatArrayElements(array, &isCopy);
       res = PyList_New(hi - lo);
       for (Py_ssize_t i = lo; i < hi; i++)
         PyList_SET_ITEM(res, i - lo, PyFloat_FromDouble(val[i]));

       JPEnv::getJava()->ReleaseFloatArrayElements(array, val, JNI_ABORT);
       return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseFloatArrayElements(array, val, JNI_ABORT); } );
}

//----------------------------------------------------------

jarray JPDoubleType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewDoubleArray(sz);
}

HostRef* JPDoubleType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.d = JPEnv::getJava()->GetStaticDoubleField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPDoubleType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.d = JPEnv::getJava()->GetDoubleField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPDoubleType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.d = JPEnv::getJava()->CallStaticDoubleMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPDoubleType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.d = JPEnv::getJava()->CallNonvirtualDoubleMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPDoubleType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jdouble val = convertToJava(obj).d;
    JPEnv::getJava()->SetStaticDoubleField(c, fid, val);
}

void JPDoubleType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jdouble val = convertToJava(obj).d;
    JPEnv::getJava()->SetDoubleField(c, fid, val);
}

vector<HostRef*> JPDoubleType::getArrayRange(jarray a, int start, int length)
{
    jdoubleArray array = (jdoubleArray)a;    
    jdouble* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetDoubleArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.d = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseDoubleArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseDoubleArrayElements(array, val, JNI_ABORT); } );
}

void JPDoubleType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jdoubleArray array = (jdoubleArray)a;
    jdouble* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetDoubleArrayElements(array, &isCopy);

        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];

            val[start+i] = convertToJava(pv).f;
        }
        JPEnv::getJava()->ReleaseDoubleArrayElements(array, val, 0);
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseDoubleArrayElements(array, val, JNI_ABORT); })
}

void JPDoubleType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{
	// use memory buffer of sequence type if available, to avoid copies.
	if (setViaBuffer<double>(a, start, length, sequence))
		return;

	jdoubleArray array = (jdoubleArray)a;
	vector<jdouble> val;
	val.reserve(length);
	// fill temporary array
	for (Py_ssize_t i = 0; i < length; ++i) {
		PyObject* o = PySequence_GetItem(sequence, i);
		jdouble d = (jdouble) PyFloat_AsDouble(o);
		Py_DecRef(o);
		if (d == -1.) { CONVERSION_ERROR_HANDLE; }
		val[i] = d;
	}

	// set java array
	try {
		JPEnv::getJava()->SetDoubleArrayRegion(array, start, length, val.data());
	} RETHROW_CATCH();
}

HostRef* JPDoubleType::getArrayItem(jarray a, int ndx)
{
    jdoubleArray array = (jdoubleArray)a;
    jdouble val;
    
    try {
        JPEnv::getJava()->GetDoubleArrayRegion(array,ndx, 1, &val);
        jvalue v;
        v.d = val;

        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPDoubleType::setArrayItem(jarray a, int ndx , HostRef* obj)
{
    jdoubleArray array = (jdoubleArray)a;
    jdouble val;
    
    try {
        val = convertToJava(obj).d;
        JPEnv::getJava()->SetDoubleArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}

PyObject* JPDoubleType::getArrayRangeToSequence(jarray a, int lo, int hi) {
    jdoubleArray array = (jdoubleArray)a;
    jdouble* val = NULL;
    jboolean isCopy;
    PyObject* res = NULL;

    try {
       val = JPEnv::getJava()->GetDoubleArrayElements(array, &isCopy);
       res = PyList_New(hi - lo);
       for (Py_ssize_t i = lo; i < hi; i++)
         PyList_SET_ITEM(res, i - lo, PyFloat_FromDouble(val[i]));

       JPEnv::getJava()->ReleaseDoubleArrayElements(array, val, JNI_ABORT);
       return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseDoubleArrayElements(array, val, JNI_ABORT); } );
}

//----------------------------------------------------------


jarray JPCharType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewCharArray(sz);
}

HostRef* JPCharType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.c = JPEnv::getJava()->GetStaticCharField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPCharType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.c = JPEnv::getJava()->GetCharField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPCharType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.c = JPEnv::getJava()->CallStaticCharMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPCharType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.c = JPEnv::getJava()->CallNonvirtualCharMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPCharType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jchar val = convertToJava(obj).c;
    JPEnv::getJava()->SetStaticCharField(c, fid, val);
}

void JPCharType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jchar val = convertToJava(obj).c;
    JPEnv::getJava()->SetCharField(c, fid, val);
}

vector<HostRef*> JPCharType::getArrayRange(jarray a, int start, int length)
{
    jcharArray array = (jcharArray)a;    
    jchar* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetCharArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.c = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseCharArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseCharArrayElements(array, val, JNI_ABORT); } );
}

void JPCharType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jcharArray array = (jcharArray)a;    
    jchar* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetCharArrayElements(array, &isCopy);
        
        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];
            
            val[start+i] = convertToJava(pv).c;            
        }
        JPEnv::getJava()->ReleaseCharArrayElements(array, val, 0);        
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseCharArrayElements(array, val, JNI_ABORT); } );
}

void JPCharType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{
	jcharArray array = (jcharArray)a;
	jchar* val = NULL;
	jboolean isCopy;

	if(setViaBuffer<jchar>(array, start, length, sequence))
		return;

	try {
		val = JPEnv::getJava()->GetCharArrayElements(array, &isCopy);
		for (Py_ssize_t i = 0; i < length; ++i) {
			PyObject* o = PySequence_GetItem(sequence, i);
			jchar c = (jchar) PyInt_AsLong(o);
			Py_DecRef(o);
			if(c == -1) { CONVERSION_ERROR_HANDLE; }
			val[start+i] = c;
		}
		JPEnv::getJava()->ReleaseCharArrayElements(array, val, 0);
	}
	RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseCharArrayElements(array, val, JNI_ABORT); } );
}

HostRef* JPCharType::getArrayItem(jarray a, int ndx)
{
    jcharArray array = (jcharArray)a;
    jchar val;

    try {
        JPEnv::getJava()->GetCharArrayRegion(array, ndx, 1, &val);
        jvalue v;
        v.c = val;

        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPCharType::setArrayItem(jarray a, int ndx , HostRef* obj)
{
    jcharArray array = (jcharArray)a;
    jchar val;
    
    try {
        val = convertToJava(obj).c;
        JPEnv::getJava()->SetCharArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}

PyObject* JPCharType::getArrayRangeToSequence(jarray a, int start, int length) {
    jcharArray array = (jcharArray)a;
    jchar* val = NULL;
    jboolean isCopy;
    PyObject* res = NULL;
    try {
       val = JPEnv::getJava()->GetCharArrayElements(array, &isCopy);
       if (sizeof(Py_UNICODE) == sizeof(jchar))
       {
           res = PyUnicode_FromUnicode((const Py_UNICODE *) val + start,
                                        length);
       }
       else
       {
           res = PyUnicode_FromUnicode(NULL, length);
           Py_UNICODE *pchars = PyUnicode_AS_UNICODE(res);

           for (Py_ssize_t i = start; i < length; i++)
               pchars[i] = (Py_UNICODE) val[i];
       }

       JPEnv::getJava()->ReleaseCharArrayElements(array, val, JNI_ABORT);
       return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseCharArrayElements(array, val, JNI_ABORT); } );
}

//----------------------------------------------------------


jarray JPBooleanType::newArrayInstance(int sz)
{
    return JPEnv::getJava()->NewBooleanArray(sz);
}

HostRef* JPBooleanType::getStaticValue(jclass c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.z = JPEnv::getJava()->GetStaticBooleanField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPBooleanType::getInstanceValue(jobject c, jfieldID fid, JPTypeName& tgtType) 
{
    jvalue v;
    v.z = JPEnv::getJava()->GetBooleanField(c, fid);
    
    return asHostObject(v);
}

HostRef* JPBooleanType::invokeStatic(jclass claz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.z = JPEnv::getJava()->CallStaticBooleanMethodA(claz, mth, val);
    return asHostObject(v);
}

HostRef* JPBooleanType::invoke(jobject obj, jclass clazz, jmethodID mth, jvalue* val)
{
    jvalue v;
    v.z = JPEnv::getJava()->CallNonvirtualBooleanMethodA(obj, clazz, mth, val);
    return asHostObject(v);
}

void JPBooleanType::setStaticValue(jclass c, jfieldID fid, HostRef* obj) 
{
    jboolean val = convertToJava(obj).z;
    JPEnv::getJava()->SetStaticBooleanField(c, fid, val);
}

void JPBooleanType::setInstanceValue(jobject c, jfieldID fid, HostRef* obj) 
{
    jboolean val = convertToJava(obj).z;
    JPEnv::getJava()->SetBooleanField(c, fid, val);
}

vector<HostRef*> JPBooleanType::getArrayRange(jarray a, int start, int length)
{
    jbooleanArray array = (jbooleanArray)a;    
    jboolean* val = NULL;
    jboolean isCopy;
    
    try {
        val = JPEnv::getJava()->GetBooleanArrayElements(array, &isCopy);
        vector<HostRef*> res;
        
        jvalue v;
        for (int i = 0; i < length; i++)
        {
            v.z = val[i+start];
            HostRef* pv = asHostObject(v);
            res.push_back(pv);
        }
        JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, JNI_ABORT);
        
        return res;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, JNI_ABORT); } );
}

void JPBooleanType::setArrayRange(jarray a, int start, int length, vector<HostRef*>& vals)
{
    jbooleanArray array = (jbooleanArray)a;
    jboolean* val = NULL;
    jboolean isCopy;

    try {
        val = JPEnv::getJava()->GetBooleanArrayElements(array, &isCopy);
        
        for (int i = 0; i < length; i++)
        {
            HostRef* pv = vals[i];
            
            val[start+i] = convertToJava(pv).z;
        }
        JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, 0);
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, JNI_ABORT); } );
}

void JPBooleanType::setArrayRange(jarray a, int start, int length, PyObject* sequence)
{
	if(setViaBuffer<bool>(a, start, length, sequence))
		return;

	jbooleanArray array = (jbooleanArray) a;
	jboolean isCopy;
	jboolean* val = NULL;
	try {
		val = JPEnv::getJava()->GetBooleanArrayElements(array, &isCopy);
		for (Py_ssize_t i = 0; i < length; ++i) {
			PyObject* o = PySequence_GetItem(sequence, i);
			jboolean c = (jboolean) PyInt_AsLong(o);
			Py_DecRef(o);
			if(c == -1) { CONVERSION_ERROR_HANDLE; }
			val[start+i] = c;
		}
		JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, 0);
	}
	RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, JNI_ABORT); } );

}

HostRef* JPBooleanType::getArrayItem(jarray a, int ndx)
{
    jbooleanArray array = (jbooleanArray)a;
    jboolean val;
    
    try {
        JPEnv::getJava()->GetBooleanArrayRegion(array, ndx, 1, &val);
        jvalue v;
        v.z = val;
        return asHostObject(v);
    }
    RETHROW_CATCH();
}

void JPBooleanType::setArrayItem(jarray a, int ndx , HostRef* obj)
{
    jbooleanArray array = (jbooleanArray)a;
    
    try {
        jboolean val = convertToJava(obj).z;
        JPEnv::getJava()->SetBooleanArrayRegion(array, ndx, 1, &val);
    }
    RETHROW_CATCH();
}

PyObject* JPBooleanType::getArrayRangeToSequence(jarray a, int start, int length) {
    jbooleanArray array = (jbooleanArray)a;
    jboolean* val = NULL;
    jboolean isCopy;

    try {
       val = JPEnv::getJava()->GetBooleanArrayElements(array, &isCopy);

       PyObject *list = PyList_New(length);
       jboolean *buf = (jboolean *) val;

       for (Py_ssize_t i = start; i < length; i++) {
           jboolean value = buf[i];
           PyObject *obj = value ? Py_True : Py_False;
           PyList_SET_ITEM(list, i, obj);
       }

       JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, 0);
       return list;
    }
    RETHROW_CATCH( if (val != NULL) { JPEnv::getJava()->ReleaseBooleanArrayElements(array, val, JNI_ABORT); } );
}

//----------------------------------------------------------


package jpype.properties;

interface ISomething {
	void foo();
}
class AbstractSomething implements ISomething {
	private int dim;
	public AbstractSomething(int dim) {
		this.dim = dim;
	}
	public void foo() {
		// default impl
	}
}

public class TestProp {

    public static ISomething factory(int[] set1)
    {
        class impl extends AbstractSomething
        {
            int[] set1;
            public impl(int[] _set1)
            {
                super((_set1.length * (_set1.length-1)) / 2);
                set1 = _set1;
            }
            public void foo()
            {
                System.out.println("hi there");
            }
        }
        return new impl(set1);
    }
    
    public static void main(String[] args) {
    	ISomething t  = TestProp.factory(new int[] {1,2,3});
    	t.foo();
    }
    
}
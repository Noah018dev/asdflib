from types import FunctionType, LambdaType
from typing import Any, Union, Optional, TypeVar, Callable
from threading import Thread, active_count
import functools

PR = TypeVar('PR')
PFR = TypeVar('PFR')

Miliseconds = int

class PromiseNotReturned(RuntimeError) :
    pass

class Promise() :
    def __init__(self, Function : Union[FunctionType, LambdaType] | PR | Callable[..., PFR], FunctionArguments : Optional[tuple] = None, FunctionKeywordArguments : Optional[dict] = None, Retries : Optional[int] = 3, WaitOnPromiseToExit : bool = False, WrapExceptions = True) :
        self.__Retries = Retries
        self.__TotalRetries = Retries
        self.__Function = Function
        self.__FunctionArguments = FunctionArguments
        self.__FunctionKeywordArguments = FunctionKeywordArguments
        self.__WrapExceptions = WrapExceptions
        if FunctionArguments is None :
            self.__FunctionArguments = ()
        if FunctionKeywordArguments is None :
            self.__FunctionKeywordArguments = {}
        self.__InternalPromiseThread = Thread(target = self.__PromiseThreadWrapper, args=self.__FunctionArguments, kwargs=self.__FunctionKeywordArguments, name=f'{Function.__name__}{active_count}', daemon=not WaitOnPromiseToExit)
        self.__InternalPromiseThread.start()
        
        ArgumentsString = ''
        KwargumentsString = ''
        
        if FunctionArguments is not None :
            ArgumentsString = ", ".join(repr(Arg) for Arg in FunctionArguments)
        if FunctionKeywordArguments is not None :
            KwargumentsString = ", ".join(f"{Key} = {Value!r}" for Key, Value in FunctionKeywordArguments.items())
        AllArguments = ", ".join(filter(None, [ArgumentsString, KwargumentsString]))
        
        self.__Represent = lambda: f'{Function.__name__}({AllArguments})'
    
    def __PromiseThreadWrapper(self, *Arguments : Optional[tuple[Any]], **KeywordArguments : Optional[dict[str, Any]]) -> None :
        if self.__WrapExceptions :
            try :
                self.__Result = self.__Function(*Arguments, **KeywordArguments)
                self.__Failed = False
            except Exception as e :
                if self.__Retries > 0 :
                    self.__Retries -= 1
                    self.__PromiseThreadWrapper(*Arguments, **KeywordArguments)
                else :
                    self.__Result = e
                    self.__Failed = True
        else :
            if self.__Retries > 1 :
                try :
                    self.__Result = self.__Function(*Arguments, **KeywordArguments)
                    self.__Failed = False
                except :
                    self.__Retries -= 1
                    self.__PromiseThreadWrapper(*Arguments, **KeywordArguments)
            else :
                self.__Result = self.__Function(*Arguments, **KeywordArguments)
    
    def __repr__(self) -> str:
        return self.__Represent()
    
    def __enter__(self):
        return self
    
    def __exit__(self, ExceptionName, ExceptionValue, ExceptionTraceback):
        if ExceptionName != None :
            return False
        
        self.WaitOn()
    
    @property
    def Arguments(self) -> Optional[tuple] :
        return self.__FunctionArguments
    
    @property
    def KeywordArguments(self) -> Optional[dict] :
        return self.__FunctionKeywordArguments
    
    @property
    def Function(self) -> PR :
        return self.__Function
    
    @property
    def IsRunning(self) -> bool :
        return self.__InternalPromiseThread.is_alive()
    
    @property
    def Result(self) -> PFR :        
        if not self.IsRunning :
            if self.__Failed :
                raise self.__Result.with_traceback(self.__Result.add_note(f'Function {repr(self)} failed after {self.__TotalRetries}. Exception above.'))
            else :
                return self.__Result
        else :
            raise PromiseNotReturned("Promise is still active!")
    
    def WaitOn(self, Timeout : Optional[Miliseconds] = None) -> PFR :
        if Timeout is None :
            self.__InternalPromiseThread.join()
        else :
            self.__InternalPromiseThread.join(timeout=Timeout / 1000)

        return self.Result
    
    
    def HasFailed(self) -> bool :
        return self.__Failed
    
    def Discard(self) -> None :
        self.__InternalPromiseThread.daemon = True
        self.__Retries = 0
        self.__TotalRetries = 0
        del self
    
    def __del__(self) :
        self.Discard()
    
    def HasSucceeded(self) -> bool :
        return not self.HasFailed()
    
    
    def __bool__(self) -> bool :
        return self.HasSucceeded()
    
    def __call__(self, *Arguments : Optional[tuple[Any]], **KeywordArguments : Optional[dict[str, Any]]) -> PFR :
        return self.WaitOn(*Arguments, **KeywordArguments)
    
    
    def __repr__(self) -> str:
        return self.__Represent()
    
    
    @classmethod
    def __class_getitem__(cls, item) -> type :
        class PromiseWithTypeHint(Promise) :
            __result_type__ = item
        return PromiseWithTypeHint
    
    
    def __str__(self) -> str :
        return self.__repr__()
    
    def __getattr__(self, Name : str) -> Any :
        if Name in self.__dict__ :
            return self.__dict__[Name]
        else :
            raise AttributeError(f'Promise has no attribute {Name}!')

A_R = TypeVar('A_R')

def AutoPromise(Function : Union[FunctionType, LambdaType] | Callable[..., A_R], *Arguments : Optional[Any], **Kwarguments : Optional[Any]) -> A_R | "Promise" :
    return Promise(Function, FunctionArguments=Arguments, FunctionKeywordArguments=Kwarguments, Retries=0)

def Promisify(Function : Union[FunctionType, LambdaType] | Callable[..., A_R]) -> Callable[..., A_R | Promise[A_R]] :
    @functools.wraps(Function)
    def PromiseDecoratorWrapper(*Arguments : Optional[Any], **Kwarguments : Optional[Any]) -> A_R | Promise[A_R] :
        return Promise(Function, FunctionArguments=Arguments, FunctionKeywordArguments=Kwarguments)()
    return PromiseDecoratorWrapper

class _InternalFunctionWrapper() :
    def __init__(self, Function : Union[FunctionType, LambdaType] | Callable[..., A_R], *Arguments : Optional[Any], **Kwarguments : Optional[Any]) :
        self.__Function = Function
        self.__Arguments = Arguments
        self.__Kwarguments = Kwarguments
        
    def Execute(self) -> Any :
        return self.__Function(*self.__Arguments, **self.__Kwarguments)

def Unpromisify(Function : Promise, JustReturnFunction = False) -> callable :
    if JustReturnFunction :
        PromiseFunction = Function.Function
        Function.Discard()
        
        return PromiseFunction
    else :
        FunctionStore = Function
        Function.Discard()
        
        return _InternalFunctionWrapper(FunctionStore.Function, *FunctionStore.Arguments, **FunctionStore.KeywordArguments).Execute


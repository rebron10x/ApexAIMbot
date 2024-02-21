import onnx 
import onnxruntime as ort
import cv2
import numpy as np
from nmsFoye import nms


class inference:

    def __init__(self,
                 #infer_mode : str,
                 thread : int,
                 model_path : str
                 ) -> None:
        #self.infer_mode = infer_mode
        self.thread = thread
        self.model_path = model_path

        self.input_name = None
        self.out_name = None
        self.onnx_session = None
        self.model = None

        self.__load_model() #运行这个加载模型的内部方法
        self.__init_model() #初始化推理会话

    def __load_model(self) -> None : #加载模型
        self.model = onnx.load(self.model_path)

    def __init_model(self) -> None : #初始化推理
        session_options = ort.SessionOptions()
        #session_options.graph_profiling = False

        provider = [
            'DmlExecutionProvider'
            # ,
            # 'CPUExecutionProvider'
        ]

        self.onnx_session = ort.InferenceSession(
            self.model.SerializePartialToString(),
            provider = provider,
            sess_options = session_options
        )

        self.input_name = self.onnx_session.get_inputs()[0].name
        self.out_name = self.onnx_session.get_outputs()[0].name
        # print('Infer pass')

    def __preprocess(self,
                     img : np.ndarray
                     ) -> np.ndarray : #前处理
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = img.transpose(2,0,1)
        img = img.astype(dtype=np.float32) / 255.0
        img = np.expand_dims(img,axis=0)
        return img

    def infer(self,
              img : np.ndarray) -> np.ndarray : #推理方法
        img = self.__preprocess(img)
        img = self.onnx_session.run(
            [self.out_name],
            {self.input_name : img}
        )[0]

        result = nms(img, 0.4, 0.5, 0.25)
        
        return result
    
if __name__ == "__main__" :
    infer = inference(
            thread = 4,
            model_path = '_apex416.onnx'
    )

    img = cv2.imread('1.jpg')
    result = infer.infer(img)
    print(result)
        
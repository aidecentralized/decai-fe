import onnx
import numpy as np
import onnx.helper as helper
import onnx.numpy_helper as numpy_helper

# Define input tensor (2-element vector)
input_tensor = helper.make_tensor_value_info('input', onnx.TensorProto.FLOAT, [1, 2])

# Define output tensor (1-element vector)
output_tensor = helper.make_tensor_value_info('output', onnx.TensorProto.FLOAT, [1, 1])

# Create a node (Matrix multiplication)
node = helper.make_node(
    'MatMul',         # Operator name
    ['input', 'weights'],  # Inputs: input tensor and weights
    ['output'],       # Output
)

# Define weights for the MatMul operation
weights = np.array([[0.5], [0.5]], dtype=np.float32)  # 2x1 weight matrix
weights_initializer = numpy_helper.from_array(weights, name='weights')

# Create the graph (which includes the operator, input, output, and weights)
graph = helper.make_graph(
    [node],                      # Nodes in the graph
    'simple_model',               # Graph name
    [input_tensor],               # Input tensor(s)
    [output_tensor],              # Output tensor(s)
    [weights_initializer],        # Initializers (weights, biases, etc.)
)

# Create the ONNX model
model = helper.make_model(graph, producer_name='simple_test_model')

# Save the model to a file
onnx.save(model, 'simple_test_model.onnx')
print('ONNX model created and saved as simple_test_model.onnx')

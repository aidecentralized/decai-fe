export async function loadOnnxModel() {
    // Fetch the ONNX model as binary data
    const response = await fetch('/simple_test_model.onnx'); // Ensure the path is correct
    const buffer = await response.arrayBuffer();  // ONNX model in binary format
    return buffer;
  }
  
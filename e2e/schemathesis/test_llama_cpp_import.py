from llama_cpp import Llama


def test_llama_cpp_import():
    """Sanity check that llama_cpp is importable and can construct a model instance.

    NOTE: Update `model_path` to point to an actual .gguf model file available
    in your environment before running this test.
    """
    model = Llama(
        model_path="/Users/lucian.cernauteanuthinslices.com/Documents/LLM Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf",  # TODO: replace with real path
        n_ctx=128,
    )

    # Simple assertion that the model object was created
    assert model is not None

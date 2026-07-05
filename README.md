# BitVector

The `BitVector.py` module is for a memory-efficient packed representation of bit
vectors and for the processing of such vectors.

If you wish, you can execute the code in `BitVector.py` directly in this
directory prior to the installation of the module. This will execute all of the
example code in the module file.

To see a working example of the `BitVector` module, see the file:

- [`examples/BitVectorDemo.py`](examples/BitVectorDemo.py)

This is a fork from Avi Kak's BitVector 3.5.0.

## Development

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management
and [`pre-commit`](https://pre-commit.com/) to enforce code quality and
conventional commit messages.

After cloning the repository, set up the development environment and register
both pre-commit and commit-msg git hooks:

```bash
uv sync
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

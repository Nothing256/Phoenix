# Double Standard Evidence: Same Code, Different Labels

These are cases where nearly identical code within the same project
receives opposite labels (good vs bad), proving that vulnerability
is context-dependent, not a property of code syntax alone.

---


## [mruby] Similarity: 1.000

| | Good (IDX 253515) | Bad (IDX 195295) |
|---|---|---|
| **Label** | ✅ Good (target=0) | ❌ Bad (target=1) |
| **CVE** | CVE-2022-0717 | CVE-2022-1276 |
| **CWE** | ['CWE-125'] | ['CWE-125'] |
| **Commit** | codegen.c: fix a argument generation bug in array assignment.... | codegen.c: need to pack argument when `n==13` too.

Because we have extra 2 argu... |
| **File** | None | codegen.c |
| **Code Length** | 3886 chars | 3885 chars |

### Code Comparison (first 30 lines)

**Good version** (IDX 253515):
```c
gen_assignment(codegen_scope *s, node *tree, node *rhs, int sp, int val)
{
  int idx;
  int type = nint(tree->car);

  switch (type) {
  case NODE_GVAR:
  case NODE_ARG:
  case NODE_LVAR:
  case NODE_IVAR:
  case NODE_CVAR:
  case NODE_CONST:
  case NODE_NIL:
  case NODE_MASGN:
    if (rhs) {
      codegen(s, rhs, VAL);
      pop();
      sp = cursp();
    }
    break;

  case NODE_COLON2:
  case NODE_CALL:
  case NODE_SCALL:
    /* keep evaluation order */
    break;

  case NODE_NVAR:
    codegen_error(s, "Can't assign to numbered parameter");
    break;
// ... (148 more lines)
```

**Bad version** (IDX 195295):
```c
gen_assignment(codegen_scope *s, node *tree, node *rhs, int sp, int val)
{
  int idx;
  int type = nint(tree->car);

  switch (type) {
  case NODE_GVAR:
  case NODE_ARG:
  case NODE_LVAR:
  case NODE_IVAR:
  case NODE_CVAR:
  case NODE_CONST:
  case NODE_NIL:
  case NODE_MASGN:
    if (rhs) {
      codegen(s, rhs, VAL);
      pop();
      sp = cursp();
    }
    break;

  case NODE_COLON2:
  case NODE_CALL:
  case NODE_SCALL:
    /* keep evaluation order */
    break;

  case NODE_NVAR:
    codegen_error(s, "Can't assign to numbered parameter");
    break;
// ... (148 more lines)
```

### Key Differences
**No differences found in first 50 lines!**

---

## [tensorflow] Similarity: 0.999

| | Good (IDX 269330) | Bad (IDX 195343) |
|---|---|---|
| **Label** | ✅ Good (target=0) | ❌ Bad (target=1) |
| **CVE** | CVE-2021-37651 | CVE-2022-21730 |
| **CWE** | ['CWE-476'] | ['CWE-125'] |
| **Commit** | Validate dimensions of input tensor in `FractionalAvgPoolGrad`

PiperOrigin-RevI... | Add negative bound check for row and column pooling_sequence in FractionalAvgPoo... |
| **File** | fractional_avg_pool_op.cc | fractional_avg_pool_op.cc |
| **Code Length** | 7257 chars | 7263 chars |

### Code Comparison (first 30 lines)

**Good version** (IDX 269330):
```c
  void Compute(OpKernelContext* context) override {
    // Here's the basic idea:
    // Batch and depth dimension are independent from row and col dimension. And
    // because FractionalAvgPool currently only support pooling along row and
    // col, we can basically think of this 4D tensor backpropagation as
    // operation of a series of 2D planes.
    //
    // For each element of a 'slice' (2D plane) of output_backprop, we need to
    // figure out its contributors when doing FractionalAvgPool operation. This
    // can be done based on row_pooling_sequence, col_pooling_seq and
    // overlapping.
    // Once we figure out the original contributors, we just need to evenly
    // divide the value of this element among these contributors.
    //
    // Internally, we divide the out_backprop tensor and store it in a temporary
    // tensor of double type. And cast it to the corresponding type.
    typedef Eigen::Map<const Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic>>
        ConstEigenMatrixMap;
    typedef Eigen::Map<Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic>>
        EigenDoubleMatrixMap;

    // Grab the inputs.
    const Tensor& orig_input_tensor_shape = context->input(0);
    OP_REQUIRES(context,
                orig_input_tensor_shape.dims() == 1 &&
                    orig_input_tensor_shape.NumElements() == 4,
                errors::InvalidArgument("original input tensor shape must be"
                                        "1-dimensional and 4 elements"));
    const Tensor& out_backprop = context->input(1);
    const Tensor& row_seq_tensor = context->input(2);
// ... (111 more lines)
```

**Bad version** (IDX 195343):
```c
  void Compute(OpKernelContext* context) override {
    // Here's the basic idea:
    // Batch and depth dimension are independent from row and col dimension. And
    // because FractionalAvgPool currently only support pooling along row and
    // col, we can basically think of this 4D tensor backpropagation as
    // operation of a series of 2D planes.
    //
    // For each element of a 'slice' (2D plane) of output_backprop, we need to
    // figure out its contributors when doing FractionalAvgPool operation. This
    // can be done based on row_pooling_sequence, col_pooling_seq and
    // overlapping.
    // Once we figure out the original contributors, we just need to evenly
    // divide the value of this element among these contributors.
    //
    // Internally, we divide the out_backprop tensor and store it in a temporary
    // tensor of double type. And cast it to the corresponding type.
    typedef Eigen::Map<const Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic>>
        ConstEigenMatrixMap;
    typedef Eigen::Map<Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic>>
        EigenDoubleMatrixMap;

    // Grab the inputs.
    const Tensor& orig_input_tensor_shape = context->input(0);
    OP_REQUIRES(context,
                orig_input_tensor_shape.dims() == 1 &&
                    orig_input_tensor_shape.NumElements() == 4,
                errors::InvalidArgument("original input tensor shape must be"
                                        "1-dimensional and 4 elements"));
    const Tensor& out_backprop = context->input(1);
    const Tensor& row_seq_tensor = context->input(2);
// ... (111 more lines)
```

### Key Differences
**No differences found in first 50 lines!**

---

## [tensorflow] Similarity: 0.998

| | Good (IDX 232405) | Bad (IDX 195410) |
|---|---|---|
| **Label** | ✅ Good (target=0) | ❌ Bad (target=1) |
| **CVE** | CVE-2021-37647 | CVE-2022-21736 |
| **CWE** | ['CWE-476'] | ['CWE-476'] |
| **Commit** | Prevent nullptr deref in SparseTensorSliceDataset

The arguments must determine ... | Properly validate sparse tensor in `SparseTensorSliceDataset`

Existing validati... |
| **File** | sparse_tensor_slice_dataset_op.cc | sparse_tensor_slice_dataset_op.cc |
| **Code Length** | 2915 chars | 2921 chars |

### Code Comparison (first 30 lines)

**Good version** (IDX 232405):
```c
  void MakeDataset(OpKernelContext* ctx, DatasetBase** output) override {
    // Create a new SparseTensorSliceDatasetOp::Dataset, insert it in
    // the step container, and return it as the output.
    const Tensor* indices;
    OP_REQUIRES_OK(ctx, ctx->input("indices", &indices));
    const Tensor* values;
    OP_REQUIRES_OK(ctx, ctx->input("values", &values));
    const Tensor* dense_shape;
    OP_REQUIRES_OK(ctx, ctx->input("dense_shape", &dense_shape));

    OP_REQUIRES(ctx, TensorShapeUtils::IsMatrix(indices->shape()),
                errors::InvalidArgument(
                    "Input indices should be a matrix but received shape ",
                    indices->shape().DebugString()));

    const auto num_indices = indices->NumElements();
    const auto num_values = values->NumElements();
    if (num_indices == 0 || num_values == 0) {
      OP_REQUIRES(ctx, num_indices == num_values,
                  errors::InvalidArgument(
                      "If indices or values are empty, the other one must also "
                      "be. Got indices of shape ",
                      indices->shape().DebugString(), " and values of shape ",
                      values->shape().DebugString()));
    }
    OP_REQUIRES(ctx, TensorShapeUtils::IsVector(values->shape()),
                errors::InvalidArgument(
                    "Input values should be a vector but received shape ",
                    indices->shape().DebugString()));
    OP_REQUIRES(ctx, TensorShapeUtils::IsVector(dense_shape->shape()),
// ... (28 more lines)
```

**Bad version** (IDX 195410):
```c
  void MakeDataset(OpKernelContext* ctx, DatasetBase** output) override {
    // Create a new SparseTensorSliceDatasetOp::Dataset, insert it in
    // the step container, and return it as the output.
    const Tensor* indices;
    OP_REQUIRES_OK(ctx, ctx->input("indices", &indices));
    const Tensor* values;
    OP_REQUIRES_OK(ctx, ctx->input("values", &values));
    const Tensor* dense_shape;
    OP_REQUIRES_OK(ctx, ctx->input("dense_shape", &dense_shape));

    OP_REQUIRES(ctx, TensorShapeUtils::IsMatrix(indices->shape()),
                errors::InvalidArgument(
                    "Input indices should be a matrix but received shape ",
                    indices->shape().DebugString()));

    const auto num_indices = indices->NumElements();
    const auto num_values = values->NumElements();
    if (num_indices == 0 || num_values == 0) {
      OP_REQUIRES(ctx, num_indices == num_values,
                  errors::InvalidArgument(
                      "If indices or values are empty, the other one must also "
                      "be. Got indices of shape ",
                      indices->shape().DebugString(), " and values of shape ",
                      values->shape().DebugString()));
    }
    OP_REQUIRES(ctx, TensorShapeUtils::IsVector(values->shape()),
                errors::InvalidArgument(
                    "Input values should be a vector but received shape ",
                    indices->shape().DebugString()));
    OP_REQUIRES(ctx, TensorShapeUtils::IsVector(dense_shape->shape()),
// ... (28 more lines)
```

### Key Differences
```diff
--- GOOD (IDX 232405)
+++ BAD (IDX 195410)
@@ -42,3 +42,3 @@
     for (int64_t i = 0; i < indices->dim_size(0); ++i) {
-      int64_t next_batch_index = indices->matrix<int64>()(i, 0);
+      int64_t next_batch_index = indices->matrix<int64_t>()(i, 0);
       OP_REQUIRES(
```

---

## [ImageMagick6] Similarity: 0.998

| | Good (IDX 439114) | Bad (IDX 210692) |
|---|---|---|
| **Label** | ✅ Good (target=0) | ❌ Bad (target=1) |
| **CVE** | CVE-2019-13133 | CVE-2018-18024 |
| **CWE** | ['CWE-401'] | ['CWE-835'] |
| **Commit** | Fix ultra rare but potential memory-leak... | https://github.com/ImageMagick/ImageMagick/issues/1337... |
| **File** | bmp.c | bmp.c |
| **Code Length** | 34604 chars | 34742 chars |

### Code Comparison (first 30 lines)

**Good version** (IDX 439114):
```c
static Image *ReadBMPImage(const ImageInfo *image_info,ExceptionInfo *exception)
{
  BMPInfo
    bmp_info;

  Image
    *image;

  IndexPacket
    index;

  MagickBooleanType
    status;

  MagickOffsetType
    offset,
    start_position;

  MemoryInfo
    *pixel_info;

  register IndexPacket
    *indexes;

  register PixelPacket
    *q;

  register ssize_t
    i,
    x;
// ... (946 more lines)
```

**Bad version** (IDX 210692):
```c
static Image *ReadBMPImage(const ImageInfo *image_info,ExceptionInfo *exception)
{
  BMPInfo
    bmp_info;

  Image
    *image;

  IndexPacket
    index;

  MagickBooleanType
    status;

  MagickOffsetType
    offset,
    start_position;

  MemoryInfo
    *pixel_info;

  register IndexPacket
    *indexes;

  register PixelPacket
    *q;

  register ssize_t
    i,
    x;
// ... (948 more lines)
```

### Key Differences
**No differences found in first 50 lines!**

---

## [qemu] Similarity: 0.972

| | Good (IDX 187732) | Bad (IDX 197796) |
|---|---|---|
| **Label** | ✅ Good (target=0) | ❌ Bad (target=1) |
| **CVE** | CVE-2014-7815 | CVE-2015-5239 |
| **CWE** | ['CWE-264'] | ['CWE-703'] |
| **Commit** | vnc: sanitize bits_per_pixel from the client

bits_per_pixel that are less than ... | ui/vnc: limit client_cut_text msg payload size

currently a malicious client cou... |
| **File** | vnc.c | vnc.c |
| **Code Length** | 4695 chars | 4407 chars |

### Code Comparison (first 30 lines)

**Good version** (IDX 187732):
```c
static int protocol_client_msg(VncState *vs, uint8_t *data, size_t len)
{
    int i;
    uint16_t limit;
    VncDisplay *vd = vs->vd;

    if (data[0] > 3) {
        update_displaychangelistener(&vd->dcl, VNC_REFRESH_INTERVAL_BASE);
    }

    switch (data[0]) {
    case VNC_MSG_CLIENT_SET_PIXEL_FORMAT:
        if (len == 1)
            return 20;

        set_pixel_format(vs, read_u8(data, 4), read_u8(data, 5),
                         read_u8(data, 6), read_u8(data, 7),
                         read_u16(data, 8), read_u16(data, 10),
                         read_u16(data, 12), read_u8(data, 14),
                         read_u8(data, 15), read_u8(data, 16));
        break;
    case VNC_MSG_CLIENT_SET_ENCODINGS:
        if (len == 1)
            return 4;

        if (len == 4) {
            limit = read_u16(data, 2);
            if (limit > 0)
                return 4 + (limit * 4);
        } else
// ... (118 more lines)
```

**Bad version** (IDX 197796):
```c
static int protocol_client_msg(VncState *vs, uint8_t *data, size_t len)
{
    int i;
    uint16_t limit;
    VncDisplay *vd = vs->vd;

    if (data[0] > 3) {
        update_displaychangelistener(&vd->dcl, VNC_REFRESH_INTERVAL_BASE);
    }

    switch (data[0]) {
    case VNC_MSG_CLIENT_SET_PIXEL_FORMAT:
        if (len == 1)
            return 20;

        set_pixel_format(vs, read_u8(data, 4), read_u8(data, 5),
                         read_u8(data, 6), read_u8(data, 7),
                         read_u16(data, 8), read_u16(data, 10),
                         read_u16(data, 12), read_u8(data, 14),
                         read_u8(data, 15), read_u8(data, 16));
        break;
    case VNC_MSG_CLIENT_SET_ENCODINGS:
        if (len == 1)
            return 4;

        if (len == 4) {
            limit = read_u16(data, 2);
            if (limit > 0)
                return 4 + (limit * 4);
        } else
// ... (110 more lines)
```

### Key Differences
**No differences found in first 50 lines!**

---
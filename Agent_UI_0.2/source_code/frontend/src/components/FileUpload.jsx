const FileUpload = ({ onUploadComplete }) => {

  const handleUpload = async (files) => {
    for (let file of files) {
      const formData = new FormData();
      formData.append("file", file);

      await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
      });
    }

    if (onUploadComplete) {
      onUploadComplete();
    }
  };

  return (
    <input
      type="file"
      multiple
      accept=".txt,.pdf,.docx,.pptx,.json,.md,.png,.jpg,.jpeg"
      onChange={(e) => handleUpload(e.target.files)}
      className="text-sm text-slate-300"
    />
  );
};

export default FileUpload;

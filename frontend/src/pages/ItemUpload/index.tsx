import React, { useState } from "react";
import Header from "../../components/Header/index";
import "./style.scss";
import {
	ArrowLeftOutlined,
	PlusOutlined,
	EditOutlined,
	GatewayOutlined,
	UndoOutlined,
} from "@ant-design/icons";
import {
	Form,
	Input,
	Button,
	InputNumber,
	Row,
	Col,
	Select,
	Upload,
	Modal,
	Divider,
} from "antd";
import type { UploadFile } from "antd/es/upload/interface";
import type { RcFile, UploadProps } from "antd/es/upload";
import { ChromePicker } from "react-color";
import Background1 from "../../assets/Background1.jpg";
import Background2 from "../../assets/Background2.jpg";
import Background3 from "../../assets/Background3.jpg";
import Background4 from "../../assets/Background4.jpg";
import Background5 from "../../assets/Background5.jpg";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import ReactCrop, {
	centerCrop,
	makeAspectCrop,
	Crop,
	PixelCrop,
} from "react-image-crop";
import AreaSelector from "./areaSelecctor";
import "react-image-crop/dist/ReactCrop.css";

const ItemUpload: React.FC = () => {
	const [form] = Form.useForm();
	const { Option } = Select;
	const [previewVisible, setPreviewVisible] = useState(false);
	const [previewImage, setPreviewImage] = useState("");
	const [previewTitle, setPreviewTitle] = useState("");
	const [fileList, setFileList] = useState<UploadFile[]>([]);
	const [color, setColor] = useState("");
	const [selectedCrop, setSelectedCrop] = useState(false);
	const [crop, setCrop] = useState<Crop>();
	console.log(crop);
	const bgArray = [
		Background1,
		Background2,
		Background3,
		Background4,
		Background5,
	];

	let navigate = useNavigate();

	const getBase64 = (file: RcFile): Promise<string> =>
		new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.readAsDataURL(file);
			reader.onload = () => resolve(reader.result as string);
			reader.onerror = (error) => reject(error);
		});

	const onReset = () => {
		form.resetFields();
	};

	const handleCancel = () => setPreviewVisible(false);

	const handlePreview = async (file: UploadFile) => {
		if (!file.url && !file.preview) {
			file.preview = await getBase64(file.originFileObj as RcFile);
		}

		setPreviewImage(file.url || (file.preview as string));
		setPreviewVisible(true);
		setPreviewTitle(
			file.name || file.url!.substring(file.url!.lastIndexOf("/") + 1)
		);
	};

	const handleChange: UploadProps["onChange"] = ({ fileList: newFileList }) =>
		setFileList(newFileList);
	const uploadButton = (
		<div>
			<PlusOutlined />
			<div style={{ marginTop: 8 }}>Upload</div>
		</div>
	);

	const normFile = (e: any) => {
		if (Array.isArray(e)) {
			return e;
		}
		return e?.fileList;
	};

	const con = (e: any) => {
		return e?.fileList;
	};

	const uploadProps: UploadProps = {
		action: con,
		listType: "picture-card",
		fileList: fileList,
		showUploadList: {
			previewIcon: <EditOutlined style={{ color: "white" }} />,
		},

		onPreview: handlePreview,
		onChange: handleChange,
	};

	const handleChangeComplete = (color: any) => {
		setColor(color.hex);
	};

	const handleColorChange = (color: any, event: any) => {
		setColor(color.hex);
	};

	const processMedia = async (media: any[]) => {
		console.log(media);
		let imageArray: any[] = [];
		media.map(async (media: any, i: Number) => {
			const currentBase64 = await getBase64(media.originFileObj as RcFile);
			console.log(currentBase64);
			imageArray.push(currentBase64);
		});
		console.log(imageArray);
		return imageArray;
	};

	const onFinish = async (values: any) => {
		let imageArray: File[] = [];
		console.log(fileList);
		// imageArray = await processMedia(values.media);
		values.media.map(async (media: any, i: Number) => {
			imageArray.push(media.originFileObj as File);
		});
		console.log(imageArray);
		var formdata = new FormData();
		formdata.append("name", values.name);
		formdata.append("category", values.category);
		formdata.append("oneliner_Description", values.oneliner);
		formdata.append("detailed_description", values.description);
		formdata.append("price", values.price);
		for (let i = 0; i < imageArray.length; i++) {
			console.log(imageArray[i])
			formdata.append("image", imageArray[i]);
		}
		await axios.post("http://localhost:9000/items", formdata);

		navigate("/")

		return "done";
	};

	return (
		<div className="ItemUpload">
			<Header />
			<div className="ItemUpload__container">
				<Link to={"/ListingOptionPage"}>
					<div className="ItemUpload__container__nav">
						<ArrowLeftOutlined style={{ marginRight: "10px" }} />
						Back to Listing Option Page
					</div>
				</Link>

				<p className="ItemUpload__container__title">Item Details</p>
				<div className="ItemUpload__container__form">
					<Form layout={"vertical"} form={form} onFinish={onFinish}>
						<Form.Item
							name="name"
							label="Item Name"
							rules={[{ required: true }]}
						>
							<Input placeholder="Item Name" />
						</Form.Item>
						<Row>
							<Col span="12">
								<Form.Item
									name="price"
									label="Item Price"
									rules={[{ required: true }]}
								>
									<InputNumber
										style={{ minWidth: "90%" }}
										placeholder="Item Price"
									/>
								</Form.Item>
							</Col>
							<Col span="12">
								<Form.Item
									name="category"
									label="Item Category"
									rules={[{ required: true }]}
								>
									<Select placeholder="Item Category">
										<Option value="Books | Music">Books | Music</Option>
										<Option value="Living">Living</Option>
										<Option value="Apparel">Apparel</Option>
										<Option value="Games">Games</Option>
										<Option value="Toys">Toys</Option>
									</Select>
								</Form.Item>
							</Col>
						</Row>
						<Form.Item
							name="oneliner"
							label="One-Liner to Describe Your Item"
							rules={[{ required: true }]}
						>
							<Input placeholder="One-liner Description" />
						</Form.Item>
						<Form.Item
							name="description"
							label="More Detailed Description of Your Item"
							rules={[{ required: true }]}
						>
							<Input.TextArea
								rows={6}
								placeholder="Write something about the current quality of your item, delivery methods, etc."
							/>
						</Form.Item>

						<Form.Item
							name="media"
							label="Upload an Image/Video here to show your item! (Max. 5)"
							valuePropName="fileList"
							getValueFromEvent={normFile}
							rules={[{ required: true }]}
						>
							<Upload
								{...uploadProps}
							// action="https://www.mocky.io/v2/5cc8019d300000980a055e76"
							>
								{fileList.length >= 5 ? null : uploadButton}
							</Upload>
						</Form.Item>
						<Modal
							visible={previewVisible}
							title={"Remove Image Background"}
							footer={null}
							onCancel={handleCancel}
							className="ItemUpload__container__form__uploadModal"
						>
							{selectedCrop ? (
								<ReactCrop
									crop={crop}
									style={{ width: "400px" }}
									onChange={(c) => setCrop(c)}
								>
									<img src={previewImage} />
								</ReactCrop>
							) : (
								<img
									alt="example"
									style={{ width: "400px" }}
									src={previewImage}
								/>
							)}
							{crop ? (
								<div
									style={{
										display: "flex",
										alignItems: "center",
										flexDirection: "column",
										marginTop: "20px",
									}}
								>
									<span style={{ fontSize: "16px", fontWeight: "500" }}>
										Confirm to remove the background?
									</span>

									<Button
										type="primary"
										className="ItemUpload__container__form__uploadModal__confirmButton"
									>
										Yes
									</Button>
								</div>
							) : (
								""
							)}
							<div className="ItemUpload__container__form__uploadModal__buttonGroup">
								<GatewayOutlined
									onClick={() => {
										setSelectedCrop(!selectedCrop);
										setCrop(undefined);
									}}
									style={{ color: selectedCrop ? "black" : "#838383" }}
									className="ItemUpload__container__form__uploadModal__button"
								/>
								<UndoOutlined className="ItemUpload__container__form__uploadModal__button" />
							</div>
							{selectedCrop ? (
								<div>
									<Divider></Divider>
									<div style={{ display: "flex" }}>
										<div>
											<p className="ItemUpload__container__form__uploadModal__text">
												Select Your Background Color
											</p>
											<ChromePicker
												color={color}
												onChangeComplete={handleChangeComplete}
												onChange={handleColorChange}
											/>
										</div>
										<Divider
											type={"vertical"}
											style={{ height: "300px", margin: "20px" }}
										/>
										<div>
											<p className="ItemUpload__container__form__uploadModal__text">
												OR Choose a Background Image
											</p>
											{bgArray.map((bg, i) => {
												return (
													<img
														key={i}
														className="ItemUpload__container__form__uploadModal__bgImage"
														src={bg}
													></img>
												);
											})}
										</div>
									</div>
								</div>
							) : (
								""
							)}
						</Modal>
						<Form.Item>
							<Button
								htmlType="submit"
								type="primary"
								className="ItemUpload__container__form__submitButton"
							>
								List Now!
							</Button>
							<Button
								htmlType="button"
								onClick={onReset}
								className="ItemUpload__container__form__resetButton"
							>
								Reset
							</Button>
						</Form.Item>
					</Form>
				</div>
			</div>
		</div>
	);
};

export default ItemUpload;

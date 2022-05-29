import React from "react";
import mercariLogo from "../../assets/mercariLogo.png";
import { Button, Avatar } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import "./style.scss";

const Header: React.FC = () => {
	let navigate = useNavigate();
	return (
		<div className="Header">
			<div>
				<Link to="/">
					<img className="Header__logo" src={mercariLogo} alt="" />
				</Link>
			</div>
			<div>
				<Button type="primary" className="Header__button" onClick={() => navigate("/ListingOptionPage")}>
					List an Item
				</Button>
				<Avatar icon={<UserOutlined />} />
			</div>
		</div >
	);
};

export default Header;

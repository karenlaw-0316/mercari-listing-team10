import React, { useState, useEffect } from "react";
import Header from "../../components/Header";
import "./style.scss";
import { ArrowLeftOutlined, CameraOutlined, EditOutlined, AmazonOutlined, QuestionOutlined } from "@ant-design/icons";
import { Button, Card } from "antd";
import { Link, useNavigate } from "react-router-dom";

const server = process.env.API_URL || 'http://127.0.0.1:9000';
const USER_ID = 1;

const { Meta } = Card;

interface purchasedItem {
    historyId: number;
    itemName: string;
    imageFilename: string;
    sourceName: string;
}

const ListingOptionPage: React.FC = () => {
    const [items, setItems] = useState<purchasedItem[]>([])
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate();

    const fetchItems = () => {
        fetch(server.concat(`/user-external-history/${USER_ID}`),
            {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log('GET success:', data);
                setItems(data['purchased items']);
                setLoading(false);
            })
            .catch(error => {
                console.error('GET error:', error)
            })
    };

    const getBrandLogo = (brandName: string) => {
        switch (brandName) {
            case 'Amazon':
                return <AmazonOutlined style={{ color: "#EF8C3B" }} />;
            default:
                return <QuestionOutlined />;
        }
    }

    useEffect(() => {
        fetchItems();
    }, []);


    return (
        <div className="ListingOptionPage">
            <Header />
            <div className="ListingOptionPage__container">
                <Link to={"/"}>
                    <div className="ListingOptionPage__container__nav">
                        <ArrowLeftOutlined style={{ marginRight: "10px" }} />
                        Back to Home
                    </div>
                </Link>

                <p className="ListingOptionPage__container__title">Start listing by...</p>
                <div className="ListingOptionPage__container__cards">
                    <Card
                        className="ListingOptionPage__container__cards__optionOne"
                        hoverable
                        style={{ width: 240 }}
                        cover={
                            <CameraOutlined style={{ fontSize: '72px' }} />
                        }
                        onClick={() => navigate("/ItemUpload")}
                    >
                        <Meta title="Upload an image" />
                    </Card>

                    <Card
                        className="ListingOptionPage__container__cards__optionTwo"
                        hoverable
                        style={{ width: 240 }}
                        cover={
                            <EditOutlined style={{ fontSize: '72px' }} />
                        }
                    >
                        <Meta title="Fill in item details" />
                    </Card>

                    <Card className="ListingOptionPage__container__cards__pastPurchases" title="Past Purchases" headStyle={{ fontSize: "1.2rem", color: "#AB2718", fontWeight: "bold", textAlign: "center" }}>
                        {
                            loading ?
                                <div>loading...</div> :
                                (items.length > 0 ?
                                    items.map(item =>
                                        <div className="ListingOptionPage__container__cards__pastPurchases__item" key={item.historyId}>
                                            <div className="ListingOptionPage__container__cards__pastPurchases__item__picture" style={{
                                                backgroundImage: `url(${server}/image/${item.imageFilename})`
                                            }}></div>
                                            <div className="ListingOptionPage__container__cards__pastPurchases__item__details">
                                                <div className="ListingOptionPage__container__cards__pastPurchases__item__details__name">{item.itemName} {getBrandLogo(item.sourceName)}</div>
                                                <div className="ListingOptionPage__container__cards__pastPurchases__item__details__price">$200</div>
                                                <div className="ListingOptionPage__container__cards__pastPurchases__item__details__people">30 people are searching for this!</div>
                                            </div>
                                            <div className="ListingOptionPage__container__cards__pastPurchases__item__button" onClick={() => navigate(`/ItemUpload?purchasedItemId=${item.historyId}`)}>
                                                List this item
                                            </div>
                                        </div>) :
                                    <div>No items here!</div>)
                        }

                        <div className="ListingOptionPage__container__cards__pastPurchases__showMore">Show more...</div>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default ListingOptionPage;
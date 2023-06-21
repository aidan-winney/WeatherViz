use reqwest::Client;
use tokio::fs::File;
use tokio::io::AsyncWriteExt;

fn lon_to_x(lon: f64, zoom: u32) -> u32 {
    let n = 2.0_f64.powi(zoom as i32);
    ((lon + 180.0) / 360.0 * n).floor() as u32
}

fn lat_to_y(lat: f64, zoom: u32) -> u32 {
    let n = 2.0_f64.powi(zoom as i32);
    let lat_rad = lat.to_radians();
    ((1.0 - (lat_rad.tan() + (1.0 / lat_rad.cos())).ln() / std::f64::consts::PI) * n / 2.0).floor() as u32
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();

    let tileserver_url = "https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png";
    let server = "a";
    let zoom = 13;
    let latitude = 27.773056;
    let longitude = -82.639999;

    let x = lon_to_x(longitude, zoom);
    let y = lat_to_y(latitude, zoom);

    let tile_url = tileserver_url
        .replace("{s}", server)
        .replace("{z}", &zoom.to_string())
        .replace("{x}", &x.to_string())
        .replace("{y}", &y.to_string());

    let mut response = client.get(&tile_url).send().await?;

    if response.status().is_success() {
        let mut file = File::create("map.png").await?;
        while let Some(chunk) = response.chunk().await? {
            file.write_all(&chunk).await?;
        }
        println!("Map image downloaded successfully.");
    } else {
        eprintln!("Error: {}", response.status());
    }

    Ok(())
}

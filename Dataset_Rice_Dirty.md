1. Arah nilai evaluasi model
Metrik	Nilai yang diharapkan	Penjelasan
MAE	Semakin mendekati 0	Rata-rata selisih absolut antara prediksi dan harga sebenarnya semakin kecil.
MSE	Semakin mendekati 0	Rata-rata kuadrat kesalahan prediksi semakin kecil. Kesalahan besar mendapat penalti lebih besar.
R²	Semakin mendekati 1	Model semakin baik dalam menjelaskan variasi harga pada data yang diuji.

R² tidak selalu berada di antara 0 dan 1. Nilai negatif bisa muncul jika model lebih buruk daripada metode sederhana yang selalu memprediksi rata-rata harga pada data pengujian.

2. Penjelasan berdasarkan jurnal ilmiah
Saya menemukan dua jurnal yang sesuai untuk mendukung penjelasan evaluasi model regresi kamu.

Jurnal 1: Chicco, Warrens, dan Jurman (2021)
Judul: The Coefficient of Determination R-squared Is More Informative than SMAPE, MAE, MAPE, MSE and RMSE in Regression Analysis Evaluation.

Jurnal ini menjelaskan bahwa MAE, MSE, dan RMSE memiliki nilai terbaik 0, dan nilainya dapat meningkat tanpa batas ketika kesalahan prediksi semakin besar. Sementara itu, R² yang mendekati 1 menunjukkan prediksi yang semakin baik, sedangkan R² negatif menunjukkan performa yang buruk dibandingkan prediksi menggunakan rata-rata nilai aktual. 
PMC+1
Jurnal 2: Willmott dan Matsuura (2005)

Judul: Advantages of the Mean Absolute Error (MAE) over the Root Mean Square Error (RMSE) in Assessing Average Model Performance.
Jurnal ini membahas penggunaan MAE dan RMSE untuk menilai kesalahan prediksi. MAE mengukur rata-rata kesalahan absolut, sedangkan RMSE memberikan bobot lebih besar terhadap kesalahan yang besar. Keduanya dinilai berdasarkan skala data, sehingga tidak memiliki patokan universal bahwa nilainya harus mendekati 1. 
doi.org+1


3. Bagaimana dengan hasil model harga beras kamu?
Berdasarkan hasil evaluasi notebook sebelumnya, hasilnya sebagai berikut.
Algoritma	MAE	MSE	R²
Linear Regression	14,73	1.280,53	-0,063
Random Forest	14,89	1.295,28	-0,075
Decision Tree	16,71	1.367,60	-0,135

Linear Regression memiliki MAE dan MSE paling rendah serta R² paling tinggi di antara ketiga model. Jadi, Linear Regression merupakan model terbaik di antara tiga model yang diuji, tetapi hasilnya belum menunjukkan performa prediksi yang baik karena nilai R² masih negatif.

Nilai R² negatif tidak berarti kodingan kamu pasti salah. Itu menunjukkan model belum mampu mengungguli patokan prediksi rata-rata pada data pengujian. Kita perlu memeriksa kualitas fitur, pola data, dan proses preprocessing sebelum menyimpulkan penyebabnya.
    <script>
    function removeFromPlaylist(episode_id, playlist_id) {
    // Get the CSRF token from the meta tag
    const csrf_token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Create the data to send in the request body as JSON
    const data = {
        episode_id: episode_id,
        playlist_id: playlist_id
    };

    // Send the POST request with the data
    fetch('/remove_from_playlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Indicate that we're sending JSON data
            'X-CSRFToken': csrf_token // Include the CSRF token
        },
        body: JSON.stringify(data) // Send the data as a JSON string
    })
        .then(response => {
            if (response.status === 200) {
                alert('Episode removed from playlist successfully!');
                return { status: 200, data: response.json() };
            } else if (response.status === 404) {
                throw new Error('Playlist or episode not found.');
            } else if (response.status === 400) {
                throw new Error('Bad request. Please check the data and try again.');
            } else if (response.status === 500) {
                alert('There is a slight inconvenience, please try again later.');
                throw new Error('Server error occurred.');
            } else {
                throw new Error(`Unexpected response: ${response.status}`);
            }
        })
        .then(async (result) => {
            const data = await result.data; // Wait for the JSON to parse
            console.log(data); // Log the response data (if needed)
        })
        .catch(error => {
            // Handle errors
            console.error('Error:', error);
            alert(`Error: ${error.message}`);
        });
}

    </script>



                <!-- Interactive Heart (Favorite) Icon -->
        <div class="favorite-icon mb-3">
    <i class="fas fa-heart" id="favorite-icon-1" style="color: #bdc3c7; cursor: pointer;"></i>
</div>
<!-- Rating Section -->
<div class="rating-container">
    <div class="rating-stars" id="rating-1">
        <i class="fas fa-star" data-index="1" style="cursor: pointer; color: #bdc3c7;"></i>
        <i class="fas fa-star" data-index="2" style="cursor: pointer; color: #bdc3c7;"></i>
        <i class="fas fa-star" data-index="3" style="cursor: pointer; color: #bdc3c7;"></i>
        <i class="fas fa-star" data-index="4" style="cursor: pointer; color: #bdc3c7;"></i>
        <i class="fas fa-star" data-index="5" style="cursor: pointer; color: #bdc3c7;"></i>
    </div>
    <div id="rating-value-1">Rating: 0/5</div>
</div>


    function addToPlaylist(episode_id, playlist_id) {
    // Get the CSRF token from the meta tag
    const csrf_token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Create the data to send in the request body as JSON
    const data = {
        episode_id: episode_id,
        playlist_id: playlist_id
    };

    // Send the POST request with the data
    fetch('/add_to_playlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Indicate that we're sending JSON data
            'X-CSRFToken': csrf_token // Include the CSRF token
        },
        body: JSON.stringify(data) // Send the data as a JSON string
    })
        .then(response => {
            if (response.status === 200) {
                alert('Episode already exists in the playlist!');
                return { status: 200, data: response.json() };
            } else if (response.status === 201) {
                alert('Episode added to the playlist successfully!');
                return { status: 201, data: response.json() };
            } else if (response.status === 400) {
                throw new Error('Bad request. Please check the data and try again.');
            } else if (response.status === 404) {
                throw new Error('Playlist or episode not found.');
            } else if (response.status === 500) {
                alert('There is a slight inconvenience, please try again later.');
                throw new Error('Server error occurred.');
            } else {
                throw new Error(`Unexpected response: ${response.status}`);
            }
        })
        .then(async (result) => {
            const data = await result.data; // Wait for the JSON to parse
            console.log(data); // Log the response data (if needed)
        })
        .catch(error => {
            // Handle errors
            console.error('Error:', error);
            alert(`Error: ${error.message}`);
        });
}
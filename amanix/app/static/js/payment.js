function formatCardNumber(input) {
    // Remove all non-digit characters (including spaces)
    let cardNumber = input.value.replace(/\D/g, '');
    
    // Group the digits in sets of 4 and add spaces after every 4 digits
    let formattedNumber = cardNumber.match(/.{1,4}/g)?.join('-') || '';
    
    // Set the formatted number back to the input
    input.value = formattedNumber;
}
function replaceNumbers(input) {
// Replace all numeric characters with an empty string
input.value = input.value.replace(/[0-9]/g, '');

}
